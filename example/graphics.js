class SVG_Graphics {
	constructor(svg_context) {
		this._svg_ = svg_context;

		this.point_style = "fill:red";
		this.line_style = "stroke: rgb(0, 0, 0);stroke-width: 0.5;fill: transparent";
		this.vertex_style = "stroke: black;stroke-width: 0.2;fill: transparent;";
		this.circle_style = "stroke: red; stroke-width: 0.5;fill: transparent;";
	}


	draw_points(points, st) {

        let r = 2;
        let txt = "";

		for (const p of points) {
			txt += "<circle cx=" + p.x + " cy=" + p.y +" r=" + r +"></circle>";
        }


        let point_group = document.createElementNS(
			"http://www.w3.org/2000/svg",
			"g"
		);
		point_group.setAttribute("style", st);
		point_group.innerHTML = txt;
		this._svg_.appendChild(point_group);

	}

	draw_lines(edges) {

		let linesSVG = "";

		for (const e of edges) {
            if(e && e.end && e.start){
			linesSVG += "<line x1=" + e.end.x + " y1=" +e.end.y +" x2=" + e.start.x + " y2=" +e.start.y+"></line>";}
		}

		let line_group = document.createElementNS(
			"http://www.w3.org/2000/svg",
			"g"
		);
		line_group.setAttribute("style", this.line_style);
		line_group.innerHTML = linesSVG;
		this._svg_.appendChild(line_group);
	
	}

	draw_circles(maxCircles){
        let linesSVG = "";

        for (let i = 0; i < maxCircles.x.length; ++i) {
            const x = maxCircles.x[i]
            const y = maxCircles.y[i]
            linesSVG += "<circle cx=" + x + " cy=" + y + " r=" + maxCircles.radius + "></circle>";
        }

        let line_group = document.createElementNS(
            "http://www.w3.org/2000/svg",
            "g"
        );

        line_group.setAttribute("style", this.circle_style);
        line_group.innerHTML = linesSVG;
        this._svg_.appendChild(line_group);
    }


	draw(p,v,e,mc){
		this._svg_.textContent = '';
		// gr.draw_points(v, this.vertex_style);
		this.draw_points(p,this.point_style);
		this.draw_lines(e);
		this.draw_circles(mc);
	}
}