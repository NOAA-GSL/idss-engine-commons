/*********************************************************************************
  * Copyright (c) 2022 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons.aspect;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class UnitsTest {

    @Test
    void shouldNotAllowInvalidType() {
        assertThrows(IllegalArgumentException.class, () -> Units.get("1.21 gigawatts"));
    }

    @Test
    void canGetSpelledOutType() {
        Units units = Units.get("Catagory");
        assertEquals(Units.Cat, units);
    }

}
