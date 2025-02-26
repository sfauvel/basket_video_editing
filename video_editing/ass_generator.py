class AssGenerator():

    def _style_header(self):
        return """[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""        

    def _code_style(self, name, alignment, margin_left, margin_right):
        def style_line(name, opacities, alignment, margin_left, margin_right):
            (opacity1, opacity2) = opacities
            return f"Style: {name:>7},  Arial,20,&H{opacity1}00FFFF,&H{opacity1}FFFF00,&H{opacity1}303030,&H{opacity2}000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, {alignment} ,{margin_right},{margin_left},5,0"
        
        lines = [style_line(name, ("00", "80"), alignment, margin_left, margin_right)] + \
                [style_line(f"{name}{index+1}", opacities, alignment, margin_left, margin_right) 
                    for (index, opacities) in enumerate([("55", "A0"), ("99", "C0"), ("BB", "F0"), ("DD", "FD")])]
            
        return "\n".join(lines)

    def style(self):
        return self._style_header() + """
Style: TeamA,   Arial,14,&H00FFFFFF,&H00FFFFFF,&H00303030,&H80000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 9 ,0,222,8,0
Style: TeamB,   Arial,14,&H00FFFFFF,&H00FFFFFF,&H00303030,&H80000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 7 ,222,0,8,0
Style: Quarter, Arial, 6,&H0000FFFF,&H00FFFF00,&H00303030,&H80000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 8 ,0,0,5,0
Style: Score,   Arial,20,&H0000FFFF,&H00FFFF00,&H00303030,&H80000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 8 ,0,0,5,0

""" + self._code_style("ScoreA", 9, 200, 0) + "\n\n" + self._code_style("ScoreB", 7, 0, 200)
