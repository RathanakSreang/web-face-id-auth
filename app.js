var fs = require('fs');
var express = require("express");
var app = new express();
// Set port, default 8888
var port = process.env.PORT || 8888;
// Use HTTPS (SSL) ?.. Default yes
var ssl = (process.env.SSL == null || process.env.SSL != 0) ? 1:0;
if(ssl==1) {
  var https = require('https');
  var server = https.createServer(
{key: fs.readFileSync('/var/ssl/cert.key'),cert: fs.readFileSync('/var/ssl/cert.crt')}, app);
  console.log("Use SSL");
} else {
  var server = require('http').createServer(app);
console.log("Start HTTP");
}
var io = require("socket.io")(server);

//io.set('origins', 'mdewo.com:'+port);
var Log = require("log"),
  log = new Log("debug");


app.use(express.static( __dirname + "/public" ));

app.get("/", function(req, res) {
  res.redirect("index.html");
});

server.listen(port, function() {
  log.info("Listening port %s", port);
});

io.on("connection", function(socket) {
  log.info("New client");
  socket.on("stream", function(img) {
    socket.broadcast.emit("stream", img);
  });
});
