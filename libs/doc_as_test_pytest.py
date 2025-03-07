import json
import os
import pytest
import re
import textwrap
from approvaltests.pytest.py_test_namer import PyTestNamer
from approvaltests.approvals import set_default_reporter,verify
from approvaltests.reporters import PythonNativeReporter



@pytest.fixture(scope="function")
def doc(request, doc_module):

    
    if request.cls is not None and request.cls not in doc_module.test_classes:
        doc_module.test_classes.append(request.cls)
        # TODO The method test is not launch if the class test fails. It's a problem.
        doc_module.verify_class(request)

    yield doc_module

    doc_module.verify_function(request)

@pytest.fixture(scope="module")
def doc_module(request):
    doc = DocAsTest()

    yield doc

    doc.verify_module(request)

class DocAsTest():
    def __init__(self):
        self.content = ""
        self.test_includes = []
        self.test_classes = []
        set_default_reporter(PythonNativeReporter())
        

    def increment_leveloffset(self):
        self.leveloffset += 1

    def decrement_leveloffset(self):
        self.leveloffset -= 1

    @staticmethod
    def camel_case_to_snake_case(match_obj):
            return match_obj.group(1) + "_" + match_obj.group(2).lower()


    def format_to_title(self, name):
        title = name
        title = re.sub(r"([a-z])([A-Z])", DocAsTest.camel_case_to_snake_case, title)
        title = title[len("test_"):]
        title = title.replace("_", " ")
        title = title[0].upper() + title[1:]
        return title

    def module_content(self, request, description):
        file_base_name = os.path.splitext(os.path.basename(request.node.name))[0]
        title = self.format_to_title(file_base_name)

        includes = "\n".join(test for test in self.test_includes)
        
        description_to_add = description.strip() + "\n\n" if description is not None else ""
        header = ":toc: left"

        return "= " + title + "\n" + header + "\n" + description_to_add + includes

    def class_content(self, request, description):
        title = self.format_to_title(request.cls.__name__)

        description_to_add = textwrap.dedent(description) +"\n\n" if description != None else ""

        return "= " + title + "\n\n" + description_to_add

    def test_content(self, request, description):

        title = self.format_to_title(request.node.name)

        description_to_add = description.strip() +"\n\n" if description != None else ""

        return  "= " + title + "\n\n" + description_to_add + self.content
            

    def register_test(self, namer):
        test = namer.get_approved_filename(namer.get_file_name())
        class_name = namer.ClassName
        class_leveloffset = len(class_name.split(".")) if class_name is not None else 0
        method_leveloffset = 1 if isinstance(namer, DocAsTestFunctionNamer) else 0
        self.test_includes.append("include::{}[leveloffset=+{}]".format(test, class_leveloffset+method_leveloffset))

    def write(self, text):
        self.content = self.content + text


    def verify_function(self, request):
       
        namer = DocAsTestFunctionNamer(request)
        
        description = request.function.__doc__

        self.register_test(namer)
        content_to_verify = self.test_content(request, description)
        self.content = ""
        verify(
            content_to_verify, 
            namer=namer
        )


    def verify_class(self, request):
        namer = DocAsTestClassNamer(request)

        description = "" if request.cls.__doc__ is None else textwrap.dedent(request.cls.__doc__)

        self.register_test(namer)

        content_to_verify = self.class_content(request, description)

        self.content = ""
        verify(
            content_to_verify, 
            namer=namer
        )


    def verify_module(self, request):
        namer = DocAsTestModuleNamer(request)

        description = request.module.__doc__

        verify(
            self.module_content(request, description), 
            namer = namer
        )

class DocAsTestNamer(PyTestNamer):
    Directory = ''
    ModuleName = ''
    
    def __init__(self, request):
        PyTestNamer.__init__(self, request, ".adoc")
        self.config = None
        self.ModuleName = request.module.__name__
        self.Directory = request.fspath.dirname

    def get_directory(self):
        return os.path.join(self.Directory, "docs")

    def config_directory(self):
        return self.Directory
    
    def get_config(self):
        """lazy load config when we need it, then store it in the instance variable self.config"""
        if self.config is None:
            config_file = os.path.join(self.config_directory(), 'approvaltests_config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {}
        return self.config


class DocAsTestFunctionNamer(DocAsTestNamer):
    
    MethodName = ''
    ClassName = ''
    def __init__(self, request):
        super().__init__(request)

        self.MethodName = request.node.name
        self.ClassName = None if request.cls is None else request.cls.__qualname__

    def get_file_name(self):
        class_name = "" if (self.ClassName is None) else ("." + self.ClassName)
        method_name = self.MethodName\
            .replace("[","_")\
            .replace("]", "_")\
            .replace(" ", "_")
        return self.ModuleName + class_name + "." + method_name
    
    def get_method_name(self):
        return self.MethodName
    
    def get_class_name(self):
        return self.ClassName

class DocAsTestClassNamer(DocAsTestNamer):
    ClassName = ''
    def __init__(self, request):
        super().__init__(request)

        self.ClassName = request.cls.__qualname__

    def get_file_name(self):
        return self.ModuleName + "." + self.ClassName

    def get_class_name(self):
        return self.ClassName
class DocAsTestModuleNamer(DocAsTestNamer):
    
    def get_file_name(self):
        return self.ModuleName
