var coordinates = []; 

function FindPosition(oElement) {
    if (typeof(oElement.offsetParent) != "undefined") {
        for (var posX = 0, posY = 0; oElement; oElement = oElement.offsetParent) {
            posX += oElement.offsetLeft;
            posY += oElement.offsetTop;
        }
        return [posX, posY];
    } else {
        return [oElement.x, oElement.y];
    }
}

function GetCoordinates(e) {
    var PosX = 0;   
    var PosY = 0;
    var ImgPos;
    ImgPos = FindPosition(myImg);
    if (!e) var e = window.event;
    if (e.pageX || e.pageY) {
        PosX = e.pageX;
        PosY = e.pageY;
    } else if (e.clientX || e.clientY) {
        PosX = e.clientX + document.body.scrollLeft +
            document.documentElement.scrollLeft;
        PosY = e.clientY + document.body.scrollTop +
            document.documentElement.scrollTop;
    }
    PosX = PosX - ImgPos[0] - (myImg.width / 2);
    PosY = (ImgPos[1] + myImg.height / 2) - PosY;

    var scaledPosX = (PosX * (3 / (myImg.width / 2))).toFixed(2);
    var scaledPosY = (PosY * (3 / (myImg.height / 2))).toFixed(2);

    coordinates.push({ x: scaledPosX, y: scaledPosY });

    if (coordinates.length === 2) {
        saveCoordinatesToFile();
    }
}

function saveCoordinatesToFile() {
    var data = coordinates.map(point => `${point.x} ${point.y}`).join('\n');
    var dataURI = "data:text/plain;charset=utf-8," + encodeURIComponent(data);

    var link = document.createElement("a");
    link.setAttribute("href", dataURI);
    link.setAttribute("download", "coordinates.txt");
    link.style.display = "none";
    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    coordinates = [];
}

var myImg = document.getElementById("myImgId");
myImg.addEventListener('click', GetCoordinates);
