let points = [];

let vor, gr, _svg_; 

(function () {
	_svg_ = document.getElementById("voronoi_svg");

    vor = new VoronoiDiagram(points, _svg_.width.baseVal.value, _svg_.height.baseVal.value);    
    gr = new SVG_Graphics(_svg_);

    gr.draw(points,vor.voronoi_vertex,vor.edges);

    document.getElementById("voronoi_svg").onclick = addPoint;
	document.getElementById("reset-btn").onclick = reset;
	document.getElementById("generate-btn").onclick = generate;
    document.getElementById("txt-btn").onclick = addPointFromTxt;
})();


function reset() {
    vor.point_list = [];
    points = [];
    _svg_.textContent = '';

};

function addPointFromTxt() {
    const fileInput = document.getElementById("txt-input");
    const file = fileInput.files[0];
    
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const fileContent = event.target.result;  // File content as a string
            parseText(fileContent);  // Parse the points from the file content
            vor.point_list = points;
            let t0 = performance.now();
            vor.update();
            let t1 = performance.now();

            gr.draw(points,vor.voronoi_vertex,vor.edges);
            document.getElementById("timer").innerText = (t1 - t0).toFixed(2) + " ms";
        };

        // Read the file as text
        reader.readAsText(file);
    } else {
        alert('Please select a file first.');
    }
}

function parseText(fileContent) {
    points = [];
    const lines = fileContent.split('\n');
    lines.forEach(line => {
        const trimmedLine = line.trim();
        if (trimmedLine) {
            // Split each line by comma and parse the coordinates
            const [x, y] = trimmedLine.split(',').map(Number);
            if (!isNaN(x) && !isNaN(y)) {
                points.push(new Point(x,y));
            }
        }
    });
    console.log(points)
}

function addPoint(event) {
    let x = event.offsetX;
    let y = event.offsetY;

    /* Add point */
    let add = true;
    for(const p of points){
        let d = Math.sqrt((x-p.x)**2+(y-p.y)**2);
        if(d<3) add = false;
    }
    if(add)points.push(new Point(x, y));
    vor.point_list = points;


    let t0 = performance.now();

    vor.update();

    let t1 = performance.now();

    gr.draw(points,vor.voronoi_vertex,vor.edges);

    document.getElementById("timer").innerText= (t1 - t0).toFixed(2) + " ms";

};




function generate() {
	let N = parseInt(document.getElementById("generate-text").value);
    points= generatePoints(N);
    vor.point_list = points;
    let t0 = performance.now();
    vor.update();
    let t1 = performance.now();

    gr.draw(vor.point_list,vor.voronoi_vertex,vor.edges);
    document.getElementById("timer").innerText = (t1 - t0).toFixed(2) + " ms";

    
}

function generatePoints(N) {
	let W = _svg_.width.baseVal.value * 0.99;
	let H = _svg_.height.baseVal.value * 0.99;

	let points = [];
	for (i = 0; i < N; i++) {
		var pt = new Point(Math.random() * W, Math.random() * H, 2);
		var good = true;
		for (const p of points) {
			let dist = Math.sqrt((pt.x - p.x) ** 2 + (pt.y - p.y) ** 2);
			if (dist < 3) {
				good = false;
				break;
			}
		}
		good ? points.push(pt) : i--;
	}

	return points;
}