/*********************************************************************************
  * Copyright (c) 2022 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons.aspect;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class WxModelTest {

    @Test
    void shouldNotAllowInvalidType() {
        assertThrows(IllegalArgumentException.class, () -> WxModel.get("Cindy Crawford"));
    }

    @Test
    void canGetSpelledOutType() {
        WxModel wxModel = WxModel.get("Any Model");
        assertEquals(WxModel.ANY, wxModel);
    }
}
