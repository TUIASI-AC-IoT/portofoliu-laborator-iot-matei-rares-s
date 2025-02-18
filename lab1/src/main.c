#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define GPIO_OUTPUT_IO 4
#define GPIO_OUTPUT_PIN_SEL (1ULL<<GPIO_OUTPUT_IO)

void ex2() {
    int cnt = 0;
    while(1) {
        gpio_set_level(GPIO_OUTPUT_IO, 1);
        vTaskDelay(1000 / portTICK_PERIOD_MS);

        gpio_set_level(GPIO_OUTPUT_IO, 0);
        vTaskDelay(500 / portTICK_PERIOD_MS); 
        gpio_set_level(GPIO_OUTPUT_IO, 1);
        vTaskDelay(250 / portTICK_PERIOD_MS); 

        gpio_set_level(GPIO_OUTPUT_IO, 0);
        vTaskDelay(750 / portTICK_PERIOD_MS); 
        // printf("cnt: %d\n", cnt++);
        // vTaskDelay(1000 / portTICK_PERIOD_MS);
        // gpio_set_level(GPIO_OUTPUT_IO, cnt % 2);
    }
   
}

int cnt_press = 0;
void ex3(void *pvParameter){
    int last_state =0; 

    gpio_set_direction(GPIO_OUTPUT_IO, GPIO_MODE_INPUT);
    gpio_pullup_en(GPIO_BUTTON);
    while (1) {
        int current_state = gpio_get_level(GPIO_BUTTON);
    
        if (last_state == 1 && current_state == 0) {
            cnt_press++;
            printf("pressed!%d\n", cnt_press);
            vTaskDelay(200 / portTICK_PERIOD_MS); 
        }

        last_state = current_state;
        vTaskDelay(10 / portTICK_PERIOD_MS); 
    }
}

void app_main() {
    //zero-initialize the config structure.
    gpio_config_t io_conf = {};
    //disable interrupt
    io_conf.intr_type = GPIO_INTR_DISABLE;
    //set as output mode
    io_conf.mode = GPIO_MODE_OUTPUT;
    //bit mask of the pins that you want to set
    io_conf.pin_bit_mask = GPIO_OUTPUT_PIN_SEL;
    //disable pull-down mode
    io_conf.pull_down_en = 0;
    //disable pull-up mode
    io_conf.pull_up_en = 0;
    //configure GPIO with the given settings
    gpio_config(&io_conf);

    ex2();

    xTaskCreate(ex3, "ex3", 2048, NULL, 10, NULL);

}