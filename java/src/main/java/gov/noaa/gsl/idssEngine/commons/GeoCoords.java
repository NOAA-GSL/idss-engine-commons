/*********************************************************************************
  * Copyright (c) 2021 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import java.awt.Point;
import java.util.Iterator;
import java.util.Set;

public class GeoCoords implements Iterable<Point> {

    private final Set<Point> coordSet;
    private int xOffset, yOffset;
    private final byte[][] grid;
    private final boolean atLeastOne;
    
    public GeoCoords(Set<Point> coords) {
        coordSet = coords;
        grid=null;
        atLeastOne = coords.size()>0;
    }

    public GeoCoords(int xOffset, int yOffset, byte[][] grid) {
        this.xOffset = xOffset;
        this.yOffset = yOffset;
        this.grid = grid;
        coordSet = null;
        atLeastOne = new GridIterator().hasNext();
    }

    @Override
    public Iterator<Point> iterator() {
        if(coordSet != null) return coordSet.iterator();
     
        return new GridIterator();
    }

    public int atMost() {
        if(coordSet!=null) return coordSet.size();
        return grid.length*grid[0].length;
    }
    
    public boolean isEmpty() {
        return !atLeastOne;
    }
    
    class GridIterator implements Iterator<Point> {

        private int width=grid.length, height=grid[0].length;
        private int x = 0, y = 0;
        
        GridIterator() {
            findNext();
        }
      
        @Override
        public boolean hasNext() {
            return x>=0;
        }

        @Override
        public Point next() {
            if(x<0) return null;
            Point pnt = new Point(x+xOffset,y+yOffset);
            findNext();
            return pnt;
        }

        public void reset() {
            x=y=0;
            findNext();
        }
        private void findNext() {
            // if last has been found don't look any more
            if(x<0) return;
            for( ; x<width; x++) {
                for( ; y<height; y++) {
                    if(grid[x][y]>0) return;
                }
            }
            // all have been found set x to -1, indicating all done
            x=-1;
        }
    }
}
