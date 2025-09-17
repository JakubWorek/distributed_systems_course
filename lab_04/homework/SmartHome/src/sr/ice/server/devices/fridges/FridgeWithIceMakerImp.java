package sr.ice.server.devices.fridges;

import Smarthome.DevicesIsInStandbyMode;
import Smarthome.FridgeWithIceMaker;
import Smarthome.Mode;
import Smarthome.TemperatureRange;
import com.zeroc.Ice.Current;

public class FridgeWithIceMakerImp extends FridgeImp implements FridgeWithIceMaker {

    public FridgeWithIceMakerImp(String id) {
        super(id);
    }

    public FridgeWithIceMakerImp(String id, TemperatureRange temperatureRange) {
        super(id, temperatureRange);
    }

    @Override
    public void makeIce(int quantity, Current current) throws DevicesIsInStandbyMode {
        if (mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }

        try {
            Thread.sleep(quantity * 1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
