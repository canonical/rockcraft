package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

@RestController
public class TimeController {

    @GetMapping("/time")
    public Map<String, String> getCurrentTime() {
        LocalDateTime now = LocalDateTime.now();
        DateTimeFormatter formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
        String timestamp = now.format(formatter);

        Map<String, String> response = new HashMap<>();
        response.put("timestamp", timestamp);
        return response;
    }
}
