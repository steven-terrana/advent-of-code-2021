import fs from 'fs'
import Graph from 'graphology'
import gexf from 'graphology-gexf'
import {allSimplePaths, allSimpleEdgePaths} from 'graphology-simple-path'
import * as turf from '@turf/turf'

const animal = 'S'

/*
  capture directions we can head from our current location.
  for each direction, 
  * rowShift and colShift explain how to get the neighbor
  * possibleNextPipes is a list of acceptable pipes we can move to
*/
const directions = {
    north: {
      rowShift: -1,
      colShift: 0,
      possibleNextPipes: ['|', 'F', '7', animal ]
    },
    south: {
      rowShift: 1, 
      colShift: 0,
      possibleNextPipes: ['|', 'L', 'J', animal ]
    },
    east: {
      rowShift: 0, 
      colShift: 1,
      possibleNextPipes: ['-', '7', 'J', animal]
    },
    west: {
      rowShift: 0,
      colShift: -1,
      possibleNextPipes: ['-', 'L', 'F', animal]
    }
}


// for each pipe type, capture the directions the animal can move. 
const pipes = {
  '|': [ directions.north, directions.south ],
  '-': [ directions.east,  directions.west  ], 
  'L': [ directions.north, directions.east  ],
  'J': [ directions.north, directions.west  ],
  '7': [ directions.south, directions.west, ],
  'F': [ directions.south, directions.east  ],
}
// if we're on the starting square, we can move in any direction
pipes[animal] = [...Object.values(directions)]

// returns a 2D array of characters representing the field
function parseField(file){
  let field = fs.readFileSync(file, 'utf-8').split('\n')
  field = field.map( row => row.split(''))
  return field
}

// for a given pipe, inspect the neighboring pipes in the direction
// we can move and add edges if we can go from this pipe to the neighbor
function addEdges(graph, node, field){
  let p = graph.getNodeAttribute(node, 'pipe')
  for(let d of pipes[p]){
    let r = graph.getNodeAttribute(node, 'r') + d.rowShift
    let c = graph.getNodeAttribute(node, 'c') + d.colShift
    if (r < 0 || r >= field.length || c < 0 || c >= field[0].length ){
      continue
    }
    let nextPipe = field[r][c]
    if (d.possibleNextPipes.includes(nextPipe)){
      let n = graph.mergeNode(`(${c},${r})`, {
        r: r, 
        c: c, 
        pipe: nextPipe
      })
      graph.addEdge(node, n[0])
    }
  }
  return graph
}

// take a 2D array of characters (the field) and return a
// undirected graph where each coordinate is a node and the
// edges represent which neighbors the animal can move to
function createGraph(field){
  let graph = new Graph()
  let pipeOptions = Object.keys(pipes)
  field.forEach( (row, r) => {
    row.forEach( (pipe, c) => {
      let node = graph.mergeNode(`(${c},${r})`, {
        r: r,
        c: c, 
        pipe: pipe
      })
      if(pipeOptions.includes(pipe)){
        graph = addEdges(graph, node[0], field)
      }
    })
  })
  return graph
}

// export the field graph into GEXF format for visualizing
function exportGraph(graph, edges, pointsWithin, file){
  
  let graphString = gexf.write(graph, {
    formatNode: (key, attributes) => {
      let color 
      let size = 2
      if (attributes.pipe == animal){
        color = '#FF0000'
        size = 4
      }
      if (pointsWithin.includes(key)){
        color = '#ED6804'
        size = 4
      }
      return {
        label: key,
        viz: {
          x: attributes.c, 
          y: attributes.r * -1,
          color: color,
          size: size
        }
      }
    },
    formatEdge: (key, attributes) => {
      let color = "#87C4AC"
      let thickness = 5
      if (edges.includes(key)){
        color = "#930063"
        thickness = 20
      }
      return {
        viz: {
          color: color,
          thickness: thickness
        }
      }
    }
  })

  fs.writeFileSync(file, graphString)
}

function findAnimalNode(){
  return graph.findNode( node => graph.getNodeAttribute(node, 'pipe') == animal)
}

// parse the field into an undirected graph
const field = parseField('input.txt')
let graph = createGraph(field)

// find the animal in that graph
let animalNode = findAnimalNode(graph)

// find the edges representing cycles within the graph that are long enough to 
// represent a loop. There will be two of them, and they are just the same
// path in reverse order. The furthest you can get away from the start is 
// the length of the cycle divided by two.
let edges = allSimpleEdgePaths(graph, animalNode, animalNode).filter(p => p.length > 3)
console.log('Part 1: ', edges[0].length/2)

// For part 2, we need to find how many nodes are encapsulated by the cycle.
// First, we'll use TurfJS to convert the nodes to GeoJSON points.
// Then, we'll define a polygon via the coordinates of the nodes in the cycle.
// Finally, we'll use TurfJS to find nodes in the graph that are within the polygon. 
// --> apparently this calculation includes the polygon itself, so we'll subtract
//     the number of coordinates defining the polygon
let points = turf.points(graph.mapNodes( node => {
  let a = graph.getNodeAttributes(node)
  return [a.c, a.r]
}))

let path = allSimplePaths(graph, animalNode, animalNode).filter(p => p.length > 4)
let polygon = turf.polygon([path[0].map( node => {
  let a = graph.getNodeAttributes(node)
  return [a.c, a.r]
})])

let tiles = turf.pointsWithinPolygon(points, polygon)
let p = tiles.features.length - polygon.geometry.coordinates[0].length + 1
console.log('Part 2: ', p)

let tilePoints = tiles.features.map( f => f.geometry.coordinates )
let pointsWithin = tilePoints.filter(p => !path[0].includes(`(${p[0]},${p[1]})`)).map(p => `(${p[0]},${p[1]})`)

// let's get a pretty picture that shows the entire field, highlights the cycle,
// and shows which nodes are encapsulated by it.
exportGraph(graph, edges[0], pointsWithin, 'visualize/public/graph.gexf')
