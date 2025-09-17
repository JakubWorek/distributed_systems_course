package sr.ice.server.devices;

import Smarthome.Device;
import Smarthome.Mode;
import com.zeroc.Ice.Current;

public class DeviceImp implements Device {

    private final String id;

    protected Mode mode;

    public DeviceImp(String id) {
        this.id = id;
        this.mode = Mode.STANDBY;
    }

    public String getId() {
        return id;
    }

    @Override
    public String getId(Current current) {
        return id;
    }

    @Override
    public void setMode(Mode mode, Current current) {
        this.mode = mode;
    }

    @Override
    public Mode getMode(Current current) {
        return mode;
    }
}
