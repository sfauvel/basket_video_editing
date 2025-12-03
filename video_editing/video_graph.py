
from video_match import MatchPart, Score
from video_recorder import EventRecord

def display_graph(match_parts: MatchPart) -> str:
    score = Score()
    infos = [(score.team_a, score.team_b, EventRecord(0,"",0,1))]
    
    for event in [event for event in match_parts.events if event.points > 0]:
        score = score.add(event.points, event.team)
        infos += [(score.team_a, score.team_b, event)]
    
    scores = [b-a for (a,b,_) in infos]
    
    quarter_index = {}
    for (index, (_,_,record)) in enumerate(infos):
        quarter_time = record.quarter_time or 1
        quarter_index[quarter_time] = index
    
    formated_scores = "\n".join([f"{index}, {value}" for (index, value) in enumerate(scores)])
    delta_max=max(scores)
    delta_min=min(scores)
    print(f"delta_max: {delta_max}, delta_min: {delta_min}")
    
    scale_x=10
    scale_y=-5
    
    border_width=30
    margin_x=30
    height=440
    graph_x_0=border_width+margin_x
    graph_y_0=height/2+border_width
    
    
    result = """++++
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" xmlns="http://www.w3.org/2000/svg"
width="700" height="500"     style="background-color:grey">
<style>
.graph {
    stroke:rgb(200,200,200);
    stroke-width:1;
}
.curve {
    fill:none;
    stroke-width:0.05;
    marker: url(#markerCircle);
    stroke:black;
}
</style>
"""
    result += f"""
<defs>
    <marker id="markerCircle" markerWidth="8" markerHeight="8" refX="5" refY="5">
        <circle cx="5" cy="5" r="0.02" style="stroke: none; fill:#000000;"/>
    </marker>
</defs>
<svg class="graph">
    <rect fill="white" width="640" height="440" x="30" y="30"/>
    <g class="grid">
        <line x1="{graph_x_0}" x2="{graph_x_0}" y1="440" y2="60"/>
    </g>
    <g class="grid">
        <line x1="{graph_x_0}" x2="640" y1="{graph_y_0}" y2="{graph_y_0}"/>
    </g>

    <text x="300" y="50" >Ecart de points</text>
"""

    for quarter in quarter_index.values():
        result += f"""<line x1="{graph_x_0+quarter*scale_x}" x2="{graph_x_0+quarter*scale_x}" y1="440" y2="60"/>"""
        

    result += f"""
    <line x1="{graph_x_0+quarter_index[1]*scale_x}" x2="{graph_x_0+quarter_index[1]*scale_x}" y1="440" y2="60"/>
        
    <text x="35" y="{graph_y_0+delta_max*scale_y+2}">{delta_max}</text>
    <line x1="56" x2="64" y1="{graph_y_0+delta_max*scale_y}" y2="{graph_y_0+delta_max*scale_y}"/>
    <text x="35" y="{graph_y_0+delta_min*scale_y+2}">{delta_min}</text>
    <line x1="56" x2="64" y1="{graph_y_0+delta_min*scale_y}" y2="{graph_y_0+delta_min*scale_y}"/>
    
    <text x="35" y="{graph_y_0+2}">0</text>
    <line x1="60" x2="60" y1="324" y2="328"/>
    <!-- text x="634" y="349"></text-->
    <line x1="639" x2="639" y1="324" y2="328"/>
</svg>
"""

    result += f"""
<polyline style="stroke:blue" class="curve" transform="translate({graph_x_0}, {graph_y_0}) scale({scale_x} {scale_y})" points="
    {formated_scores}
"/>

</svg>
++++
        """
        
    return result