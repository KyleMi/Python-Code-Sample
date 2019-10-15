


// google map object
var map=null;
var mapCenter = null;
// dictionary object with frame number as key and latitude longtitude as value
var dict = new Object();
//Signal, switch dictionary object with milepost as key, location of signal and switch as value.
var sig_dict = new Object();
var sw_dict = new Object();

// watched frame list
var watched_ls = [];

var start_time;
var end_time;

var start_frame=0;
var end_frame=0;
var flag = false;

// our current video output have frame rate of 20
var frame_rt = 20;

// list to store current frame of cursor
var cursor_ls = [];

// Intialize the map view
google.maps.event.addDomListener(window, 'load', initialize);

// The video player's current frame of map view
var current_frame_gbl=0;


// Check status of map every 200 ms
setInterval("constant_check()", 200);


// intialize the route
function initialize() {
    // read csv data
    var readCSV = jQuery.ajax({
      url: csv,
      cache: false,
      async: false,
      dataType: 'text',
      success: function(csv_data) {
        var allRows = csv_data.split(/\r?\n|\r/);
        var item_idx = allRows[0].split(',').indexOf('LEVL');
        var mp_idx = allRows[0].split(',').indexOf('MP');
        var lat_idx = allRows[0].split(',').indexOf('LAT');
        var lng_idx = allRows[0].split(',').indexOf('LNG');

        //Find location of overhead signal, high stand signal, frog switch and turnout switch then add to sig_dict and sw_dict
        for (var singleRow = 1; singleRow < allRows.length-1; singleRow++) {
          row_token=allRows[singleRow].split(',');
          if(row_token[item_idx].indexOf('SIG_SIGNAL') != -1){
            if(row_token[item_idx].indexOf('OVERHEAD') != -1 || row_token[item_idx].indexOf('HIGH STAND') != -1){

              if(sig_dict[row_token[mp_idx]] != undefined ){
                sig_dict[row_token[mp_idx]].push([row_token[lat_idx], row_token[lng_idx]]);
              }
              else{
                sig_dict[row_token[mp_idx]] = [[row_token[lat_idx], row_token[lng_idx]]];
              }
            }
          }
          else if (row_token[item_idx].indexOf('SW_SWITCH') != -1){

            if(row_token[item_idx].indexOf('FROG') != -1 || row_token[item_idx].indexOf('TURNOUT') != -1){
              if(sw_dict[row_token[mp_idx]] != undefined ){
                sw_dict[row_token[mp_idx]].push([row_token[lat_idx], row_token[lng_idx]]);

              }
              else{
                sw_dict[row_token[mp_idx]] = [[row_token[lat_idx], row_token[lng_idx]]];
              }
            }
          }
        }
      }
    });



    // get frame number, latitude, longtitude and milepost to list
    var framenum_ls = [];
    var lat_ls = [];
    var long_ls = [];
    var mp_ls = [];

    // start and end mile post of route
    var start_mp;
    var end_mp;

    // read xml data with ajax call
    var readXML = jQuery.ajax({
      url: "xml/"+ path +".xml",
      cache: false,
      async: false,
      success: function(data) {

        // After getting all of the mile post frame number and latitude, longtitude from xml
        jQuery(data).find("sensor_data").find("megaframe_sensordata").each(function(i) {

          // Set the point we found to anything stated in the XML
          var xmlData_frame = String(jQuery(this).find("output_frame_number").text());
          framenum_ls = framenum_ls.concat(Number(xmlData_frame))

          var xmlData_mp = String(jQuery(this).find("custom_record").find('MILEPOST').text());
          var sign;
          var mile=0;
          var feet=0;
          var milepost = 0;

          //convert milepost data to unit of mile and add to mp_ls
          if (xmlData_mp.indexOf('+') != -1){
            sign = xmlData_mp.indexOf("+");

            mile = xmlData_mp.substring(0, sign);

            ft = xmlData_mp.substr(sign+1);

            milepost = Number(ft)/5280+Number(mile);
            mp_ls.push(parseFloat(milepost.toFixed(4)));
          }
          else if(xmlData_mp.indexOf("-") != -1){
            sign = xmlData_mp.indexOf("-");

            mile = xmlData_mp.substring(0, sign);
            ft = xmlData_mp.substr(sign+1);
            milepost = Number(mile)-Number(ft)/5280;
            mp_ls.push(parseFloat(milepost.toFixed(4)));
          }
          else{
            mp_ls.push(Number(xmlData_mp));
          }


          // Read and convert latitude, longtitude to form google map API can recognize
          jQuery(this).find("sensor_record").each(function() {

          var xmlData_lat = String(jQuery(this).find('rmcLatitudeLong').text());

          // Get rid of the N,W sign
          var xmlData_lat = xmlData_lat.substring(0,xmlData_lat.length -1);

          // read the string of float to number
          xmlData_lat = Number(xmlData_lat);

          //calculate the coresponding location googlemap can read
          xmlData_lat = Math.round(xmlData_lat/100)+ xmlData_lat%100/60;
          xmlData_lat = parseFloat(xmlData_lat.toFixed(6))

          var xmlData_long = String(jQuery(this).find('rmcLongitudeLong').text());

          var xmlData_long = xmlData_long.substring(0,xmlData_long.length -1);

          xmlData_long = Number(xmlData_long);

          xmlData_long = -1*Math.round(xmlData_long/100)- xmlData_long%100/60;
          xmlData_long = parseFloat(xmlData_long.toFixed(6))

          // if latitude found add it to latitude list, else get rid of the frame number
          if(xmlData_lat != 0 && xmlData_long != 0){
            lat_ls.push(xmlData_lat);
            long_ls.push(xmlData_long);
          }
          else{
            framenum_ls.pop();
          }

        });

        });

      }
    });

    //Find two ends of mile post list.
    start_mp=Math.min.apply(Math,mp_ls);
    end_mp=Math.max.apply(Math,mp_ls);



    var sig_loc = [];
    var sw_loc = [];
    // find signals falls in the range of our rout's milepost
    for(var mp in sig_dict){
      if(start_mp<=Number(mp) && Number(mp)<=end_mp){
        for(var i=0; i<sig_dict[mp].length;i++){
          var sig_lat = sig_dict[mp][i][0];
          var sig_lng = sig_dict[mp][i][1];
          var sig_lat_6 = parseFloat(sig_lat).toFixed(6);
          var sig_lng_6 = parseFloat(sig_lng).toFixed(6);
          sig_loc.push({"lat": sig_lat,"lng":sig_lng});
        }
      }
    }

    // find switch falls in the range of our rout's milepost
    for(var mp in sw_dict){
      if(start_mp<=Number(mp) && Number(mp)<=end_mp){
        for(var i=0; i< sw_dict[mp].length;i++){
          var sw_lat = sw_dict[mp][i][0];
          var sw_lng = sw_dict[mp][i][1];
          var sw_lat_6 = parseFloat(sw_lat).toFixed(6);
          var sw_lng_6 = parseFloat(sw_lng).toFixed(6);
          sw_loc.push({"lat": sw_lat,"lng":sw_lng});
        }
      }
    }

    var sig_marker_ls = [];
    var sw_marker_ls = [];


    var arrCoords = []
    ///Create the frame:[latitude,longtitude] dictionary and create arry of coordinated to plot the route
    for (var i = 0;i<lat_ls.length;i++){
      var cord_ls = [lat_ls[i], long_ls[i]];
      dict[framenum_ls[i]] = cord_ls;
      arrCoords.push(new google.maps.LatLng(lat_ls[i], long_ls[i]))
    }




    // set center of map view to be location at middle point of frame of video
    // need to read xml file first so we can dynamiclly determin center of map
    mapCenter = new google.maps.LatLng(dict[Math.ceil(Object.keys(dict).length/2)][0],dict[Math.ceil(Object.keys(dict).length/2)][1]);

    var myOptions = {
        zoom: 15,
        center: mapCenter,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    //set the map object
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

    // draw the initial route on the map
    var route = new google.maps.Polyline({
        path: arrCoords,
        strokeColor: "#00FF00",
        strokeOpacity: 1.0,
        strokeWeight: 6,
        geodesic: false,
        map: map
    });

/////////

    // draw signals, switches markers when zoomin level above or equal to 17
    // get rid of all markers if zoom level below 17
    google.maps.event.addListener(map, 'zoom_changed', function(e) {
      if(map.zoom >= 17){
        if(sig_marker_ls.length ==0 && sw_marker_ls.length==0){
          for(var i=0; i<sig_loc.length;i++){
            var marker = new google.maps.Marker({
                position: new google.maps.LatLng(sig_loc[i]["lat"],sig_loc[i]["lng"]),
                icon: 'images/signal-transparent-resized-color-0.png',
                map: map
              });
            sig_marker_ls.push(marker);
          }
          for(var i in sw_loc){

            var marker = new google.maps.Marker({
              position: new google.maps.LatLng(sw_loc[i]["lat"],sw_loc[i]["lng"]),
              icon: 'images/switch-transparent-rescale-color-0.png',
              map: map
            });
            sw_marker_ls.push(marker);
          };
        };
      }
      else{
        if(sig_marker_ls.length != 0){
          for(i = 0; i < sig_marker_ls.length; i++) {
            sig_marker_ls[i].setMap(null);
          };
          sig_marker_ls=[];
        }
        if(sw_marker_ls.length != 0){
          for(i=0;i<sw_marker_ls.length;i++) {
            sw_marker_ls[i].setMap(null);
          }
          sw_marker_ls=[];
        };
      };
    });

    // get tag videoplayer
    var videoPlayer = document.getElementById('videoPlayer');

    // click event by clicking on route polyline
    google.maps.event.addListener(route,'click', function(e) {
      //get the clicked location on the route
      var lat = parseFloat(e.latLng.lat().toFixed(6));
      var long = parseFloat(e.latLng.lng().toFixed(6));

      // find the cloest point on map and it's coresponding data frame number
      var frame = find_frame(dict,lat,long);

      videoPlayer.currentTime = frame/frame_rt;

      document.getElementById('videoPlayerContainer').style.display = "block";
      document.getElementById('relatedContainer').style.display     = "none";
      document.getElementById('videoTitle').style.maxWidth          = "800px";
      document.getElementById('buttons').style.maxWidth             = "800px";
      google.maps.event.trigger(map, 'resize');

    });

}



// check status of map module called every 200ms
function constant_check(){

  var videoPlayer = document.getElementById('videoPlayer');

  var ls = [];

  // When video is playing record time and frame player started and end
  // draw watched route with points between the frame number it started playing and paused
  if (videoPlayer.paused == false){
    // when video playing
    if (flag == false){
      // just started playing
      start_time = videoPlayer.currentTime;
      start_frame = start_time*frame_rt;
      flag = true;
    }
  }
  else{
    //when video paused
    if(flag == true){
      // just paused
      end_time = videoPlayer.currentTime;
      end_frame = end_time*frame_rt;
      for(var frame in dict){
        if (Number(frame)<Number(end_frame) && Number(frame)>Number(start_frame)){
          ls.push(new google.maps.LatLng(dict[frame][0],dict[frame][1]));
        }
      };

      var route_watched = new google.maps.Polyline({
        path: ls,
        strokeColor: "#00008B",
        strokeOpacity: 1.0,
        strokeWeight: 4,
        geodesic: false,
        map: map
      });

      // viewed route is clickable and go to frame
      google.maps.event.addListener(route_watched,'click', function(e) {
        var lat = parseFloat(e.latLng.lat().toFixed(6));
        var long = parseFloat(e.latLng.lng().toFixed(6));

        // find the cloest point on map and it's coresponding data frame number
        frame = find_frame(dict,lat,long);

        videoPlayer.currentTime = frame/frame_rt;

        document.getElementById('videoPlayerContainer').style.display = "block";
        document.getElementById('relatedContainer').style.display     = "none";
        document.getElementById('videoTitle').style.maxWidth          = "800px";
        document.getElementById('buttons').style.maxWidth             = "800px";
        google.maps.event.trigger(map, 'resize');
      });

    }
    flag = false;


    // if current frame changed clean up previous cursor data first
    if(videoPlayer.currentTime != current_frame_gbl){
      if(cursor_ls.length != 0){
        for(i = 0; i < cursor_ls.length; i++) {
          cursor_ls[i].setMap(null);
        };
        cursor_ls=[];
      }

      // make each frame number to number type so they are comparable
      var frame_srt_ls = Object.keys(dict);
      for(var i=0; i< frame_srt_ls.length;i++){
        frame_srt_ls[i]=Number(frame_srt_ls[i]);
      }

      var actualFrame;
      var nextFrame;

      // current frame to the cloest integer below it.
      var actualTime = videoPlayer.currentTime;
      actualFrame = Math.floor(Number(actualTime)*Number(frame_rt));

      // To find direction of cursor we need to find current point and point it is going to
      // find the actual frame that exist in data.
      // use for loop to compare because there are gaps of frame number in xml data (frame number not consequtive)
      for(var i=actualFrame;i<Math.max.apply(null,frame_srt_ls);i++){
        if(i in dict){
          actualFrame =i;
        }
        break;
      }

      // find the next frame number exist, if video on it's last frame use the same number for current frame and next frame
      if(actualFrame!=Math.max.apply(null,frame_srt_ls)){
        for (var i=actualFrame+1;i<Math.max.apply(null,frame_srt_ls);i++){
          if (i in dict){
            nextFrame = i;
            break;
          }
        }
      }
      else{
        nextFrame=actualFrame;
      }

      var currentloc = new google.maps.LatLng(dict[actualFrame][0],dict[actualFrame][1]);
      var nextloc = new google.maps.LatLng(dict[nextFrame][0],dict[nextFrame][1]);


      // Define a symbol using a predefined path (an arrow)
      // supplied by the Google Maps JavaScript API.
      var lineSymbol = {
        path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW
      };

      // Create the polyline and add the symbol via the 'icons' property.
      var cursor = new google.maps.Polyline({
        path: [currentloc, nextloc],
        icons: [{
          icon: lineSymbol,
          offset: '100%'
        }],
        map: map
      });
      cursor_ls.push(cursor);

      current_frame_gbl = videoPlayer.currentTime;
    }
    else if(videoPlayer.currentTime==0){
      var actualFrame;
      var nextFrame;
      var frame_srt_ls = Object.keys(dict);
      for(var i=0; i< frame_srt_ls.length;i++){
        frame_srt_ls[i]=Number(frame_srt_ls[i]);
      }
      // console.log(frame_srt_ls);
      for (var i=1;i<Math.max.apply(null,frame_srt_ls);i++){
          if (i in dict){
            actualFrame = i;
            for(var j =i+1;j<Math.max.apply(null,frame_srt_ls);j++){
              if(j in dict){
                nextFrame=j;
                break;
              }
            }
            break;
          }
      }

      var currentloc = new google.maps.LatLng(dict[actualFrame][0],dict[actualFrame][1]);
      var nextloc = new google.maps.LatLng(dict[nextFrame][0],dict[nextFrame][1]);


      // Define a symbol using a predefined path (an arrow)
      // supplied by the Google Maps JavaScript API.
      var lineSymbol = {
        path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW
      };

      // Create the polyline and add the symbol via the 'icons' property.
      var cursor = new google.maps.Polyline({
        path: [currentloc, nextloc],
        icons: [{
          icon: lineSymbol,
          offset: '100%'
        }],
        map: map
      });
      cursor_ls.push(cursor);

      current_frame_gbl = videoPlayer.currentTime;

    }
  }

}


// return cloest frame near the clicked point, default in the range within 20m
function find_frame(dict,lat,long){
  for(var loc in dict){
      var distance = google.maps.geometry.spherical.computeDistanceBetween(new google.maps.LatLng(lat,long), new google.maps.LatLng(dict[loc][0], dict[loc][1]));
      if (distance < 20){
        return loc;
      }

    };
}
