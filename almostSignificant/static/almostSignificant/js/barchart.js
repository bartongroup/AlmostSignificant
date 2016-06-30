function barchart(labelArray, valueArray, divID, inputHeight, inputWidth, inputColor) {
    /* Plot barcharts given the provided labels and values.
     * Takes the array of labels and array of values as first two arguements.
     * Next arguement is the ID of the div which the barcode is to be inserted into
     * Final two arguements are the input height and width (optional).
     * */

    var margin = {top: 30, right: 0, bottom: 0, left: 200};
    var width = inputWidth || 1000 - margin.left - margin.right;
    var height= inputHeight || 300-margin.top -margin.bottom;
    //if there are a lot of samples, make the image bigger
    //unless a size is manually specified
    if (height/valueArray.length < 20)
    {
        height= inputHeight || (20*valueArray.length)-margin.top -margin.bottom;
    }

    var selectedColor = inputColor || "teal";

    //set the y scale for the labels given the input index.
    var yScale = d3.scale.ordinal()
        .domain(labelArray.map(function(d) {return d;}))
        .rangeRoundBands([margin.top, height], 0.05);

    //set the y scale for the AXIS.
    //Needs to be different to the labels otherwise the lables break.
    var yAxisScale = d3.scale.ordinal()
        .domain(labelArray.map(function(d) {return d;}))
        .rangeRoundBands([margin.top, height], 0.05);

    //initialise the y axis
    var yAxis = d3.svg.axis().scale(yAxisScale).orient("left");

    //setup the x scale for the data.
    var xScale = d3.scale.linear()
        .domain([0, d3.max(valueArray, function(d) {return parseFloat(d); })])
        .range([margin.left,width])

    //...and initilise the x axis
    var xAxis = d3.svg.axis().scale(xScale).orient("top");

     var tooltipDiv = d3.select("body").append("div")
         .attr("class", "tooltip")
         .style("opacity", 0); //needs to be 0, as this plonks a box on the web page ready to use as tooltip
    
//    var tooltipDiv = d3.select(divID).append("div")
//        .attr("class", "tooltip")
//        .style("opacity", 0);

    //Create SVG element
    var svg = d3.select(divID)
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    //Create bars
    svg.selectAll("rect")
        .data(valueArray)
    .enter().append("rect")
        .attr("y", function(d, i) {
            return yScale(i); //note using the index so it works for repeat values
        })
        .attr("x", function(d) {
            return margin.left; //shift by the padding for the lables
        })
        .attr("height", (yScale.rangeBand())) //scale the height
        .attr("width",0)
        .transition()
        .ease("linear")
        .duration(1000)
        .attr("width", function(d) {

            return xScale(d)-margin.left; //scale the width, leaving space for the labels
        })
        .attr("fill", selectedColor) //prettify
        //.text(function(d,i){ return labelArray[i];console.log(labelArray[i]);})
        //.attr("title",function(d,i){ return labelArray[i];})
        .each("end",function(d)
            {
            d3.select(this)
            .on("mouseover", function(d) {
                d3.select(this).style("fill", "mediumSeaGreen");
                tooltipDiv.transition()
                    .duration(200)
                    .style("opacity", .9);
                tooltipDiv .html(d + "M")
                    .style("left", (d3.event.pageX + 15) + "px")
                    .style("top", (d3.event.pageY - 28) + "px");
            })
            .on("mouseout", function(d){
                d3.select(this).style("fill", selectedColor);
                tooltipDiv.transition()
                    .duration(500)
                    .style("opacity", 0);
            })
            .on("mousedown", function(d){
                if (Math.random() < 0.93)
                    {
                    d3.select(this)
                        .transition()
                        .ease("bounce")
                        .duration(2000*Math.random())
                        .attr("width", function(d) { return d/2; })
                        .each("end", function(d)
                        {
                        d3.select(this)
                            .transition()
                            .delay(1500)
                            .ease("bounce")
                            .duration(5000*Math.random())
                            .attr("width", function(d) { return xScale(d)-margin.left;});
                        });
                    }
                else
                    {
                    d3.select(this)
                        .transition()
                        .ease("back")
                        .duration(500)
                        .attr("y", height);
                    };
            })
            //.append("svg:title")
            .text(function(d,i) { return labelArray[i]; });
            });



    //add the y axis to the graph
    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + margin.left + ",0)")
        .call(yAxis);
    //and add the x axis to the graph!
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + margin.top +")")
        .call(xAxis);

    svg.append("text")
        .attr("class", "x label")
        .attr("text-anchor", "start")
        .attr("x", margin.left)
        .attr("dy", ".75em")
        .text("Millions of Reads");

}

function stackedBarchart(jsonInput, divID, inputHeight, inputWidth) {
    /* Plot barcharts given the provided labels and values. Splits the bar into two,
     * each being the entry from valueArray and value2Array.
     * Takes the array of labels and array of values as first two arguements.
     * Next arguement is the ID of the div which the barcode is to be inserted into
     * Final two arguements are the input height and width (optional).
     * */
    var margin = {top: 30, right: 0, bottom: 0, left: 150};
    var width = inputWidth || 1000 - margin.left - margin.right;
    var height= inputHeight || 400-margin.top -margin.bottom;
    //if there are a lot of samples, make the image bigger
    //unless a size is manually specified
    if (height/jsonInput.length < 20)
    {
        height= inputHeight || (20*jsonInput.length)-margin.top -margin.bottom;
    };

    //extract all of the data
    var oneHitOneLib = [];
    var manyHitOneLib = [];
    var oneHitManyLib = [];
    var manyHitManyLib = [];

    var organisms = Object.keys(jsonInput);
    for (var i = 0; i < organisms.length; i+=1) {
        currentData = jsonInput[organisms[i]];
        oneHitOneLib[i] = currentData[0];
        manyHitOneLib[i] = currentData[1];
        oneHitManyLib[i] = currentData[2];
        manyHitManyLib[i] = currentData[3];
    }
    var oneHitOneLibColor = "lightBlue";
    var manyHitOneLibColor = "blue";
    var oneHitManyLibColor = "red";
    var manyHitManyLibColor = "darkRed";
    //set the y scale for the labels given the input index.
    var yScale = d3.scale.ordinal()
        .domain(organisms.map(function(d) {return d;}))
        .rangeRoundBands([margin.top, height], 0.05);

    //set the y scale for the AXIS.
    //Needs to be different to the labels otherwise the lables break.
    var yAxisScale = d3.scale.ordinal()
        .domain(organisms.map(function(d) {return d;}))
        .rangeRoundBands([margin.top, height], 0.05);
    //initialise the y axis
    var yAxis = d3.svg.axis().scale(yAxisScale).orient("left");

    //setup the x scale for the data.
    //using 0-100 in domain as this is the range the contaminants are in (a %)
    var xScale = d3.scale.linear()
        .domain([0, 100])
        //.domain([0, d3.max(valueArray, function(d) {return parseFloat(d); })])
        .range([margin.left,width-20])

    //...and initilise the x axis
    var xAxis = d3.svg.axis().scale(xScale).orient("top");
    //Create SVG element
    var svg = d3.select(divID)
        .append("svg")
        .attr("width", width)
        .attr("height", height);

     //add the tooltip area to the webpage
     var tooltip = d3.select("body").append("div")
         .attr("class", "tooltip")
         .style("opacity", 0); //needs to be 0, as this plonks a box on the web page ready to use as tooltip
    
    //Create bars
    //oneHitOneLib
    svg.selectAll("rect1")
        .data(oneHitOneLib)
    .enter().append("rect")
        .attr("y", function(d, i) {
            return yScale(i); //note using the index so it works for repeat values
        })
        .attr("x", function(d) {
            return margin.left; //shift by the padding for the lables
        })
        .attr("height", (yScale.rangeBand())) //scale the height
        .attr("width", function(d,i) {
            return xScale(d)-margin.left; //scale the width, leaving space for the labels
        })
       .attr("fill", oneHitOneLibColor) //prettify
        .text(function(d,i){ return d;})
        .attr("title",function(d){ return d;})
        .on("mouseover", function(d,i) {
            d3.select(this).style("fill", "mediumSeaGreen");
            tooltip.transition()
            .duration(200)
            .style("opacity", 100);
            tooltip.html(d3.format(",.0f")(d) + "% of reads occur only once, only in " + organisms[i])
            .style("left", (d3.event.pageX + 15) + "px")
            .style("top", (d3.event.pageY - 28) + "px");
           })
        .on("mouseout", function(d){
            d3.select(this).style("fill", oneHitOneLibColor);
            tooltip.transition()
            .duration(500)
            .style("opacity", 0);
       });
       //oneHitManyLib
       svg.selectAll("rect2")
            .data(manyHitOneLib)
            .enter()
            .append("rect")
            .attr("y", function(d, i) {
                return yScale(i); //note using the index so it works for repeat values
            })
            .attr("x", function(d,i) {
                return xScale(oneHitOneLib[i]); //shift by the padding for the lables
            })
            .attr("height", (yScale.rangeBand())) //scale the height
            .attr("width", function(d) {
                return xScale(d)-margin.left; //scale the width, leaving space for the labels
            })
            .attr("fill", manyHitOneLibColor) //prettify
            .text(function(d){ return d;})
            .attr("title",function(d){ return d;})
            .on("mouseover", function(d,i) {
                d3.select(this).style("fill", "mediumSeaGreen");
                tooltip.transition()
                .duration(200)
                .style("opacity", 100);
                tooltip.html(d3.format(",.0f")(d) + "% of reads occur multiple times, only in " + organisms[i])
                .style("left", (d3.event.pageX + 15) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
             })
            .on("mouseout", function(d){
                d3.select(this).style("fill", manyHitOneLibColor);
                tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });
       //manyHitOneLib
       svg.selectAll("rect3")
            .data(oneHitManyLib)
            .enter()
            .append("rect")
            .attr("y", function(d, i) {
                return yScale(i); //note using the index so it works for repeat values
            })
            .attr("x", function(d,i) {
                return xScale((oneHitOneLib[i]+manyHitOneLib[i])); //shift by the padding for the lables
            })
            .attr("height", (yScale.rangeBand())) //scale the height
            .attr("width", function(d) {
                return xScale(d)-margin.left; //scale the width, leaving space for the labels
            })
            .attr("fill", oneHitManyLibColor) //prettify
            .text(function(d){ return d;})
            .attr("title",function(d){ return d;})
            .on("mouseover", function(d) {
                d3.select(this).style("fill", "mediumSeaGreen");
                tooltip.transition()
                .duration(200)
                .style("opacity", 100);
                tooltip.html(d3.format(",.0f")(d) + "% of reads occur once in multiple organisms.")
                .style("left", (d3.event.pageX + 15) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
                           })
            .on("mouseout", function(d){
                d3.select(this).style("fill", oneHitManyLibColor);
                tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });
       //manyHitManyLib
       svg.selectAll("rect3")
            .data(manyHitManyLib)
            .enter()
            .append("rect")
            .attr("y", function(d, i) {
                return yScale(i); //note using the index so it works for repeat values
            })
            .attr("x", function(d,i) {
                return xScale((oneHitOneLib[i]+manyHitOneLib[i]+oneHitManyLib[i])); //shift by the padding for the lables
            })
            .attr("height", (yScale.rangeBand())) //scale the height
            .attr("width", function(d) {
                return xScale(d)-margin.left; //scale the width, leaving space for the labels
            })
            .attr("fill", manyHitManyLibColor) //prettify
            .text(function(d){ return d;})
            .attr("title",function(d){ return d;})
            .on("mouseover", function(d) {
                d3.select(this).style("fill", "mediumSeaGreen");
                tooltip.transition()
                .duration(200)
                .style("opacity", 100);
                tooltip.html(d3.format(",.0f")(d) + "% of reads occur multipletimes in multiple organisms.")
                .style("left", (d3.event.pageX + 15) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
                           })
            .on("mouseout", function(d){
                d3.select(this).style("fill", manyHitManyLibColor);
                tooltip.transition()
                .duration(500)
                .style("opacity", 0);
       });


    //add the y axis to the graph
    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + margin.left + ",0)")
        .call(yAxis);
    //and add the x axis to the graph!
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + margin.top +")")
        .call(xAxis);

    svg.append("text")
        .attr("class", "x label")
        .attr("text-anchor", "start")
        .attr("x", margin.left)
        .attr("dy", ".75em")
        .text("Percentage of Reads");

}

function numberedBarchart(labelArray, readArray, baseArray, divID, inputHeight, inputWidth, inputColor) {
    /* Plot barcharts given the provided labels and values. Append the value of the
     * number of reads and Gbases to the end of the plot.
     * Takes the array of labels and array of values as first two arguements.
     * Next arguement is the ID of the div which the barcode is to be inserted into
     * Final two arguements are the input height and width (optional).
     * */

    var margin = {top: 30, right: 150, bottom: 0, left: 200};
    var width = inputWidth || 1500 - margin.left - margin.right;
    var height= inputHeight || 300-margin.top -margin.bottom;
    //if there are a lot of samples, make the image bigger
    //unless a size is manually specified
    if (height/readArray.length < 20)
    {
        height= inputHeight || (20*readArray.length)-margin.top -margin.bottom;
    }

    var selectedColor = inputColor || "teal";

    //set the y scale for the labels given the input index.
    var yScale = d3.scale.ordinal()
        .domain(labelArray.map(function(d) {return d;}))
        .rangeRoundBands([margin.top, height], 0.05);

    //set the y scale for the AXIS.
    //Needs to be different to the labels otherwise the lables break.
    var yAxisScale = d3.scale.ordinal()
        .domain(labelArray.map(function(d) {return d;}))
        .rangeRoundBands([margin.top, height], 0.05);

    var yLabelScale = d3.scale.ordinal()
        .domain(labelArray.map(function(d) {return d;}))
        .rangeRoundBands([margin.top, height], 0.05);

   //initialise the y axis
    var yAxis = d3.svg.axis().scale(yAxisScale).orient("left");

    //setup the x scale for the data.
    var xScale = d3.scale.linear()
        .domain([0, d3.max(readArray, function(d) {return parseFloat(d); })])
        .range([margin.left,width - margin.right])

    //...and initilise the x axis
    var xAxis = d3.svg.axis().scale(xScale).orient("top");

    var tooltipDiv = d3.select(divID).append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    //Create SVG element
    var svg = d3.select(divID)
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    //Create bars
    svg.selectAll("rect")
        .data(readArray)
    .enter().append("rect")
        .attr("y", function(d, i) {
            return yScale(i); //note using the index so it works for repeat values
        })
        .attr("x", function(d) {
            return margin.left; //shift by the padding for the lables
        })
        .attr("height", (yScale.rangeBand())) //scale the height
        .attr("width",0)
        .transition()
        .ease("linear")
        .duration(1000)
        .attr("width", function(d) {

            return xScale(d)-margin.left; //scale the width, leaving space for the labels
        })
        .attr("fill", selectedColor) //prettify
        //.text(function(d,i){ return labelArray[i];console.log(labelArray[i]);})
        //.attr("title",function(d,i){ return labelArray[i];})
        .each("end",function(d,i)
            {
            d3.select(this)
            .on("mouseover", function(d, i) {
                d3.select(this).style("fill", "mediumSeaGreen");
                tooltipDiv.transition()
                    .duration(200)
                    .style("opacity", .9);
                tooltipDiv .html(d + "M")
                .style("left", (d3.event.pageX + 15) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
            })
            .on("mouseout", function(d){
                d3.select(this).style("fill", selectedColor);
                tooltipDiv.transition()
                    .duration(500)
                    .style("opacity", 0);
            })
            .on("mousedown", function(d){
                if (Math.random() < 0.93)
                    {
                    d3.select(this)
                        .transition()
                        .ease("bounce")
                        .duration(2000*Math.random())
                        .attr("width", function(d) { return d/2; })
                        .each("end", function(d)
                        {
                        d3.select(this)
                            .transition()
                            .delay(1500)
                            .ease("bounce")
                            .duration(5000*Math.random())
                            .attr("width", function(d) { return xScale(d)-margin.left;});
                        });
                    }
                else
                    {
                    d3.select(this)
                        .transition()
                        .ease("back")
                        .duration(500)
                        .attr("y", height);
                    };
            })
            //.append("svg:title")
            .text(function(d,i) { return labelArray[i]; })
            });


    svg.selectAll("lableText")
        .data(readArray)
        .enter().append("text")
        .attr("text-anchor", "start")
        .attr("x", function(d)
            {
            return width - margin.right;
            })
        .attr("y", function(d, i)
            {
            return yLabelScale(i) + yScale.rangeBand()/2 ; //add half the bar height
            })
        .text( function(d,i)
            {
            return d + "M, " + baseArray[i] + "Gb";
            });

    //add the y axis to the graph
    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + margin.left + ",0)")
        .call(yAxis);
    //and add the x axis to the graph!
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + margin.top +")")
        .call(xAxis);

    svg.append("text")
        .attr("class", "x label")
        .attr("text-anchor", "start")
        .attr("x", margin.left)
        .attr("dy", ".75em")
        .text("Millions of Reads");

}

//    //add the y axis to the graph
//    svg.append("g")
//        .attr("class", "y axis")
//        .attr("transform", "translate(" + margin.left + ",0)")
//        .call(yAxis);
//    //and add the x axis to the graph!
//    svg.append("g")
//        .attr("class", "x axis")
//        .attr("transform", "translate(0," + margin.top +")")
//        .call(xAxis);
//
//    svg.append("text")
//        .attr("class", "x label")
//        .attr("text-anchor", "start")
//        .attr("x", margin.left)
//        .attr("dy", ".75em")
//        .text("Millions of Reads");
//

function premadeHist(valueArray,divID) {
    // Generate an Irwin–Hall distribution of 10 random variables.
//    var values = d3.range(1000).map(d3.random.irwinHall(10));
    // A formatter for counts.
    var formatCount = d3.format(",.0f");

    var margin = {top: 10, right: 30, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

    var x = d3.scale.linear()
        .domain([0, d3.max(valueArray)])
        .range([0, width]);

    // Generate a histogram using twenty uniformly-spaced bins.
    var data = d3.layout.histogram()
        .bins(x.ticks(20))
        (valueArray);

    var y = d3.scale.linear()
        .domain([0, d3.max(data, function(d) { return d.y; })])
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var svg = d3.select(divID).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var bar = svg.selectAll(".bar")
        .data(data)
        .enter().append("g")
        .attr("class", "bar")
        .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    bar.append("rect")
        .attr("x", 1)
        .attr("width", x(data[0].dx) - 1)
        .attr("height", function(d) { return height - y(d.y); })
        .attr("fill", "teal"); //prettify

    bar.append("text")
        .attr("dy", ".75em")
        .attr("y", 6)
        .attr("x", x(data[0].dx) / 2)
        .attr("text-anchor", "middle")
        .text(function(d) { if ( formatCount(d.y) > 0 ) { return formatCount(d.y)}
                        else { return ""}  });

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + "0" + "," + "0)")
        .call(yAxis);

    svg.append("text")
        .attr("class", "x label")
        .attr("text-anchor", "bottom")
        .attr("x", width/2)
        .attr("y", height + 20 )
        .attr("dy", ".75em")
        .text("Millions of Reads");

    svg.append("text")
        .attr("class", "y label")
        .attr("text-anchor", "start")
        .attr("x", -height/1.5 )
        .attr("y", -margin.left )
        .attr("dy", ".75em")
        .text("Number of Lanes")
        .attr("transform", "rotate(-90)");

}

function densityScatterGraph( valueArray, divID, xAxisLabel, yAxisLabel ) {
        //value array is array of arrays
        //each element is [clusterDensity, numReads, metadata (eg run name, lane number)
//    var margin = {top: 10, right: 30, bottom: 30, left: 40},
//    width = 960 - margin.left - margin.right,
//    height = 500 - margin.top - margin.bottom;
    var xValues = []
    var yValues = []
    var metaData = []
    var xStdDev = []
    var yStdDev = []
    for (var i = 0; i < valueArray.length; i++) {
        xValues[i] = valueArray[i][0]
        yValues[i] = valueArray[i][1]
        xStdDev[i] = valueArray[i][2]
        yStdDev[i] = valueArray[i][3]
        metaData[i] = valueArray[i][4]
    }
    console.log(divID);
    var margin = {top: 10, right: 30, bottom: 30, left: 105},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

    var x = d3.scale.linear()
       .domain([0, d3.max(xValues)])
       .range([margin.left, width - margin.right]);
    var xAxisScale = d3.scale.linear()
       .domain([0, d3.max(xValues)])
       .range([0, width - margin.right - margin.left]);
    var y = d3.scale.linear()
       .domain([0, d3.max(yValues)])
       .range([height-margin.top , margin.top]);

    var yAxisScale = d3.scale.linear()
       .domain([0, d3.max(yValues)])
       .range([height, margin.top]);

     var xAxis = d3.svg.axis()
        .scale(xAxisScale)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(yAxisScale)
        .orient("left");

    var svg = d3.select(divID)
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g");

    var tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    svg.selectAll("circle")
       .data(valueArray)
       .enter()
       .append("circle")
       .attr("cx", function(d) {
            return x(d[0]);
       })
       .attr("cy", function(d) {
            return y(d[1]);
       })
       .attr("r", 3)
        .on("mouseover", function(d) {
         d3.select(this).style("fill", "red");
         tooltip.transition()
             .duration(200)
             .style("opacity", .9);
         tooltip.html(d[4])
             .style("left", (d3.event.pageX + 15) + "px")
             .style("top", (d3.event.pageY - 28) + "px");
	     })
   		 .on("mouseout", function(d){
         d3.select(this).style("fill", "black");
         tooltip.transition()
             .duration(500)
             .style("opacity", 0);
            });
//.on("mouseover", function(d) {
//            d3.select(this).style("fill", "red");
//            tooltip.transition()
//            .duration(200)
//            .style("opacity", 100);
//            tooltip.html("<br/>" + d[4] + ". <br/>")
//            .style("left", (d3.event.pageX + 15) + "px")
//            .style("top", (d3.event.pageY - 28) + "px");
//           })
//        .on("mouseout", function(d){
//            d3.select(this).style("fill", "black");
//            tooltip.transition()
//            .duration(500)
//            .style("opacity", 0);
//		});

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(" + margin.left + "," + (height - margin.top) + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + margin.left + "," + -margin.top + ")")
        .call(yAxis);

    var yErrorBarArea = d3.svg.area()
        .x(function(d) {return x(d[0]); })
        .y0(function(d) {return y(d[1] - d[3]); })
        .y1(function(d) {return y(d[1] + d[3]); })
        .interpolate("linear");

    var xErrorBarArea = d3.svg.area()
        .x0(function(d) {return x(d[0] - d[2]); })
        .x1(function(d) {return x(d[0] + d[2]); })
        .y(function(d) {return y(d[1]); })
        .interpolate("linear");
//
//    var errorBarSVG = d3.select(divID).append("svg")
//
//    var errorBars = errorBarSVG.selectAll("path")
//             .data(data);
//
//    errorBars.enter().append("path");
//
//    errorBars.attr("d", function(d){return errorBarArea([d]);})
//    //turn the data into a one-element array
//    //and pass it to the area function
//          .attr("stroke", "red")
//          .attr("stroke-width", 1.5);
    svg.selectAll("path")
        .data(valueArray)
        .enter()
        .append("path")
        .attr("d", function(d){return yErrorBarArea([d]);})
        .attr("stroke", "red")
        .attr("stroke-width", 0.25);

    svg.selectAll("path1")
        .data(valueArray)
        .enter()
        .append("path")
        .attr("d", function(d){return xErrorBarArea([d]);})
        .attr("stroke", "blue")
        .attr("stroke-width", 0.125);

    svg.append("text")
        .attr("class", "x label")
        .attr("text-anchor", "start")
        .attr("x", width/2)
        .attr("y", height + margin.top)
        .attr("dy", ".75em")
        .text(xAxisLabel);

    svg.append("text")
        .attr("class", "y label")
        .attr("text-anchor", "start")
        .attr("x", -height/1.5 )
        .attr("dy", ".75em")
        .text(yAxisLabel)
        .attr("transform", "rotate(-90)");



}
//    svg.selectAll("text")
//        .data(valueArray)
//        .enter()
//        .append("text")
//        .text(function(d) {
//            //return x(d[0]) + "," + y(d[1]);
//            return d[2];
//        })
//        .attr("x", function(d) {
//             return x(d[0]);
//        })
//        .attr("y", function(d) {
//             return y(d[1]);
//        })
//        .attr("font-family", "sans-serif")
//        .attr("font-size", "11px")
//        .attr("fill", "red");
//    var dataset = [
//                [5, 20], [480, 90], [250, 50], [100, 33], [330, 95],
//                [410, 12], [475, 44], [25, 67], [85, 21], [220, 88]
//              ];
//    var svg = d3.select(divID)
//                .append("svg")
//                .attr("width", width)
//                .attr("height", height);
//    svg.selectAll("circle")
//       .data(dataset)
//       .enter()
//       .append("circle")
//       .attr("cx", function(d) {
//            return d[0];
//       })
//       .attr("cy", function(d) {
//            return d[1];
//       })
//       .attr("r", 5);
//}

