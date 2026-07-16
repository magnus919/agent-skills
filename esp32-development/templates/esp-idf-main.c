#include <stdbool.h>
#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Deliberately inert until OUTPUT_GPIO is replaced from the exact board schematic.
#define OUTPUT_GPIO ((gpio_num_t)-1)
#define ACTIVE_LEVEL 1
#define PERIOD_MS 500

static const char *TAG = "bringup";

void app_main(void) {
    gpio_num_t output_gpio = OUTPUT_GPIO;
    if (!GPIO_IS_VALID_OUTPUT_GPIO(output_gpio)) {
        ESP_LOGE(TAG, "set OUTPUT_GPIO to a verified output-capable pin");
        return;
    }

    // Set the inactive latch before switching the pin to output mode.
    const gpio_config_t output = {
        .pin_bit_mask = 1ULL << output_gpio,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };

    gpio_set_level(output_gpio, !ACTIVE_LEVEL);
    ESP_ERROR_CHECK(gpio_config(&output));
    ESP_LOGI(TAG, "GPIO %d configured; verify the physical signal", output_gpio);

    bool active = false;
    while (true) {
        active = !active;
        gpio_set_level(output_gpio, active ? ACTIVE_LEVEL : !ACTIVE_LEVEL);
        ESP_LOGI(TAG, "active=%d", active);
        vTaskDelay(pdMS_TO_TICKS(PERIOD_MS));
    }
}
