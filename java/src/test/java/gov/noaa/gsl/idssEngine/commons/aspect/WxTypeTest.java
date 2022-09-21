/*********************************************************************************
  * Copyright (c) 2022 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons.aspect;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class WxTypeTest {

    @Test
    void  shouldNotAllowInvalidType() {
        assertThrows(IllegalArgumentException.class, () -> WxType.get("ice_cream"));
    }

}
