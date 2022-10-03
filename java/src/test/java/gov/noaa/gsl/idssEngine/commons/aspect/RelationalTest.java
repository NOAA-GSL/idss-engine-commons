/*********************************************************************************
  * Copyright (c) 2022 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons.aspect;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class RelationalTest {

    @Test
    void shouldNotAllowInvalidType() {
        assertThrows(IllegalArgumentException.class, () -> Relational.get("penultimate"));
    }

    @Test
    void canGetSpelledOutType() {
        Relational relational = Relational.get("Greater than or equal");
        assertEquals(Relational.GREATERTHANOREQUAL, relational);
    }

    @Test
    void canGetValidFromShortName() {
        Relational relational = Relational.get(Relational.get("BETWEEN").toShortString());
        assertEquals(Relational.BETWEEN, relational);
    }
}
