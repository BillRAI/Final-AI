const http = require('http');
const { exec } = require('child_process');

const hostname = '127.0.0.1';
const port = 3000;

const server = http.createServer((req, res) => {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/plain');
    res.end('ROS command server\n');
});

server.listen(port, hostname, () => {
    console.log(`Server running at http://${hostname}:${port}/`);
});

server.on('request', (req, res) => {
    if (req.url === '/runturtlebot3') {
        exec('rosrun turtlebot3_movetogoal move2goal.py', (error, stdout, stderr) => {
            if (error) {
                console.error(`exec error: ${error}`);
                res.end('Error executing ROS command');
            } else {
                console.log(`stdout: ${stdout}`);
                console.error(`stderr: ${stderr}`);
                res.end('ROS command executed successfully');
            }
        });
    }
});
