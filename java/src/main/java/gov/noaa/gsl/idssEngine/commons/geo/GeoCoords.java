/*********************************************************************************
  * Copyright (c) 2021 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons.geo;

import java.awt.Point;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Set;

public class GeoCoords implements Iterable<Point> {

    private List<Set<Point>> coordSetList = null;
    private List<GridGeoCoords> gridCoordList = null;
    private boolean atLeastOne = false;
    private int atMost = 0;
    
    public GeoCoords(Set<Point> coordSet) {
        add(coordSet);
    }
    
    public GeoCoords(int xOffset, int yOffset, byte[][] grid) {
        add(xOffset, yOffset, grid);
    }
    
    public GeoCoords add(Set<Point> coordSet) {
        if(coordSet.size()>0) {
//System.out.println("adding Set<Point>");
            if(coordSetList == null) coordSetList = new ArrayList<>();
            coordSetList.add(coordSet);
            atLeastOne = true;
            atMost += coordSet.size();
        }
        return this;
    }

    public GeoCoords add(int xOffset, int yOffset, byte[][] grid) {
        GridGeoCoords  ggc = new GridGeoCoords(xOffset, yOffset, grid);
        if(ggc.atLeastOne) {
//System.out.println("adding grid");
            if(gridCoordList == null) gridCoordList = new ArrayList<>();
            gridCoordList.add(ggc);
            atLeastOne = true;
            atMost += grid.length*grid[0].length;
        }
        return this;
    }
    
    public boolean isEmpty()  {
        return !atLeastOne;
    }
    
    public int atMost() {
        return this.atMost;
    }
    
    @Override
    public Iterator<Point> iterator() {
        return new ListsIterator();
    }
    
    class ListsIterator implements Iterator<Point> {
        private int setIdx=-1, gridIdx=-1;
        Iterator<Point> it = null;      

        ListsIterator() {
            if(coordSetList!=null)
                setIdx = coordSetList.size();
            if(gridCoordList!=null)
                gridIdx=gridCoordList.size();
            findNext();
        }
        
        @Override
        public boolean hasNext() {
            if(it==null) return false;
           
            if(it.hasNext()) return true;

            findNext();
            return hasNext();
        }

        @Override
        public Point next() {
            if(it==null) 
                throw new NoSuchElementException();
            
            return it.next();
        }
        
        void findNext() {
            for(setIdx--; setIdx>=0; setIdx--) {
                it = coordSetList.get(setIdx).iterator();
                if(it.hasNext()) return;
            }
            
            for(gridIdx--; gridIdx>=0; gridIdx--) {
                it = gridCoordList.get(gridIdx).iterator();
                if(it.hasNext()) return;
            }
            it = null;
        }
    }
    
    class GridGeoCoords implements Iterable<Point> {
        private final int xOffset, yOffset;
        private final byte[][] grid;
        private final boolean atLeastOne;
        
    
        public GridGeoCoords(int xOffset, int yOffset, byte[][] grid) {
            this.xOffset = xOffset;
            this.yOffset = yOffset;
            this.grid = grid;
            atLeastOne = new GridIterator().hasNext();
        }
    
        @Override
        public Iterator<Point> iterator() {
            return new GridIterator();
        }
    
        public int atMost() {
            return grid.length*grid[0].length;
        }
        
        public boolean isEmpty() {
            return !atLeastOne;
        }
        
        class GridIterator implements Iterator<Point> {
    
            private int width=grid.length, height=grid[0].length;
            private int x=0, y=-1;
            
            GridIterator() {
                findNext();
            }
          
            @Override
            public boolean hasNext() {
                return x<width;
            }
    
            @Override
            public Point next() {
                if(x>=width) return null;
                Point pnt = new Point(x+xOffset,y+yOffset);
                findNext();
                return pnt;
            }
    
            public void reset() {
                x=0;
                y=-1;
                findNext();
            }
            private void findNext() {
                // if last has been found don't look any more
                if(x>=width) return;
                for(; x<width; x++, y=-1) {
                    for(y++; y<height; y++) {
                        if(grid[x][y]>0) return;
                    }
                }
            }
        }
    }
}
