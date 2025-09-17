package sr.ice.server.devices.fridges;

import Smarthome.*;
import com.zeroc.Ice.Current;
import sr.ice.server.devices.DeviceImp;

public class FridgeImp extends DeviceImp implements Fridge {

    protected final TemperatureRange temperatureRange;

    protected double temperature;

    public FridgeImp(String id) {
        super(id);
        temperatureRange = new TemperatureRange(-20, 20);
        temperature = 0;
    }

    public FridgeImp(String id, TemperatureRange temperatureRange) {
        super(id);
        this.temperatureRange = temperatureRange;
        temperature = 0;
    }

    @Override
    public void setTemperature(double temperature, Current current) throws DevicesIsInStandbyMode, InputTemperatureOutOfRange {
        if (mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }

        if (temperature < temperatureRange.min || temperature > temperatureRange.max) {
            throw new InputTemperatureOutOfRange();
        }

        this.temperature = temperature;
    }

    @Override
    public double getTemperature(Current current) throws DevicesIsInStandbyMode {
        if (mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }

        return temperature;
    }

    @Override
    public TemperatureRange getTemperatureRange(Current current) throws DevicesIsInStandbyMode {
        if (mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }

        return temperatureRange;
    }

}
