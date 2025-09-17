#ifndef SMARTHOME_ICE
#define SMARTHOME_ICE

module Smarthome
{
    enum Mode { ON, STANDBY };
    exception DevicesIsInStandbyMode {};
    exception InputTemperatureOutOfRange {};
    exception ProductDoesNotExist {};
    exception InputResolutionOutOfRange {};
    exception StorageFullError {};
    exception InvalidDate {};

    interface Device {
        idempotent string getId();

        idempotent void setMode(Mode mode);

        idempotent Mode getMode();
    };

    enum Unit {
        GRAM, KILOGRAM, LITRE, MILLILITRE
    };

    struct Date {
        int day;
        int month;
        int year;
    };

    struct Product {
        int id;
        string name;
        int amount;
        Unit unit;
        Date expirationDate;
    };

    struct TemperatureRange {
        double min;
        double max;
    };

    interface Fridge extends Device {
        idempotent void setTemperature(double temperature) throws DevicesIsInStandbyMode, InputTemperatureOutOfRange;

        idempotent double getTemperature() throws DevicesIsInStandbyMode;

        idempotent TemperatureRange getTemperatureRange() throws DevicesIsInStandbyMode;
    };

    sequence<Product> ProductList;


    interface FridgeWithProductsMonitoring extends Fridge {
        idempotent ProductList getProducts() throws DevicesIsInStandbyMode;

        idempotent Product getProduct(int id) throws DevicesIsInStandbyMode, ProductDoesNotExist;

        idempotent ProductList getExpiredProducts() throws DevicesIsInStandbyMode;

        void addProduct(Product product) throws DevicesIsInStandbyMode, InvalidDate;

        void addProducts(ProductList products) throws DevicesIsInStandbyMode, InvalidDate;

        void removeProduct(int productId) throws DevicesIsInStandbyMode, ProductDoesNotExist;
    };

    interface FridgeWithIceMaker extends Fridge {
        void makeIce(int weigth) throws DevicesIsInStandbyMode;
    };

    struct Location {
        double x;
        double y;
    };

    struct ResolutionRange {
        int min;
        int max;
    };

    interface Camera extends Device {
        idempotent Location getLocation() throws DevicesIsInStandbyMode;

        idempotent void setResolution(int resolution) throws DevicesIsInStandbyMode, InputResolutionOutOfRange, StorageFullError;

        idempotent int getResolution() throws DevicesIsInStandbyMode;

        idempotent double getStorageLevel() throws DevicesIsInStandbyMode;
    };
};
#endif