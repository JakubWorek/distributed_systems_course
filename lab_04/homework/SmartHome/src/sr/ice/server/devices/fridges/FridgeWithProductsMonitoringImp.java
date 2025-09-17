package sr.ice.server.devices.fridges;

import Smarthome.*;
import com.zeroc.Ice.Current;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

public class FridgeWithProductsMonitoringImp extends FridgeImp implements Smarthome.FridgeWithProductsMonitoring {

    private List<Product> products = new ArrayList<>();

    public FridgeWithProductsMonitoringImp(String id) {
        super(id);
    }

    public FridgeWithProductsMonitoringImp(String id, TemperatureRange temperatureRange) {
        super(id, temperatureRange);
    }

    public FridgeWithProductsMonitoringImp(String id, TemperatureRange temperatureRange, List<Product> products) {
        super(id, temperatureRange);
        this.products = products;
    }

    @Override
    public Product[] getProducts(Current current) throws DevicesIsInStandbyMode {
        if (mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }

        return products.toArray(new Product[0]);
    }

    @Override
    public Product getProduct(int id, Current current) throws DevicesIsInStandbyMode, ProductDoesNotExist {
        if (mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }

        for (Product product : products) {
            if (product.id == id) {
                return product;
            }
        }

        throw new ProductDoesNotExist();
    }

    @Override
    public Product[] getExpiredProducts(Current current) throws DevicesIsInStandbyMode {
        if (mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }

        List<Product> expiredProducts = new ArrayList<>();
        for (Product product : products) {
            int day = product.expirationDate.day;
            int month = product.expirationDate.month;
            int year = product.expirationDate.year;

            if (day < 1 || day > 31 || month < 1 || month > 12 || year < 1900) {
                continue;
            }
            Calendar calendar = Calendar.getInstance();
            int currentDay = calendar.get(Calendar.DAY_OF_MONTH);
            int currentMonth = calendar.get(Calendar.MONTH) + 1;
            int currentYear = calendar.get(Calendar.YEAR);

            if (year < currentYear || (year == currentYear && month < currentMonth) || (year == currentYear && month == currentMonth && day < currentDay)) {
                expiredProducts.add(product);
            }

        }
        return expiredProducts.toArray(new Product[0]);
    }

    @Override
    public void addProduct(Product product, Current current) throws DevicesIsInStandbyMode, InvalidDate {
        if (mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }

        int day = product.expirationDate.day;
        int month = product.expirationDate.month;
        int year = product.expirationDate.year;

        if (day < 1 || day > 31 || month < 1 || month > 12 || year < 1900) {
            throw new InvalidDate();
        }

        products.add(product);
    }

    @Override
    public void addProducts(Product[] products, Current current) throws DevicesIsInStandbyMode,  InvalidDate {
        if (mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }

        for (Product product : products) {
            int day = product.expirationDate.day;
            int month = product.expirationDate.month;
            int year = product.expirationDate.year;

            if (day < 1 || day > 31 || month < 1 || month > 12 || year < 1900) {
                throw new InvalidDate();
            }
        }

        for (Product product : products) {
            this.products.add(product);
        }
    }

    @Override
    public void removeProduct(int productId, Current current) throws DevicesIsInStandbyMode, ProductDoesNotExist {
        if (mode == Mode.STANDBY) {
            throw new DevicesIsInStandbyMode();
        }

        for (Product product : products) {
            if (product.id == productId) {
                products.remove(product);
                return;
            }
        }

        throw new ProductDoesNotExist();
    }
}
