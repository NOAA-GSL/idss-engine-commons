/*********************************************************************************
  * Copyright (c) 2022 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons.aspect;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class FieldTest {

    @Test
    void shouldNotAllowInvalidType() {
        assertThrows(IllegalArgumentException.class, () -> Field.get("Folsom"));
    }

    @Test
    void canGetSpelledOutType() {
        Field field = Field.get("Dew point");
        assertEquals(Field.TD, field);
    }

}
