package com.ksk.controller;

import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/video")
@CrossOrigin("*")
public class VideoController {

    private final String PYTHON_API = "http://127.0.0.1:8000/video/";

    @PostMapping("/generate")
    public Map<String, Object> generateVideo(@RequestBody Map<String, String> request) {

        String text = request.get("text");

        RestTemplate restTemplate = new RestTemplate();

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> body = new HashMap<>();
        body.put("text", text);

        HttpEntity<Map<String, String>> entity = new HttpEntity<>(body, headers);

        ResponseEntity<Map> response = restTemplate.postForEntity(
                PYTHON_API,
                entity,
                Map.class
        );

        return response.getBody();
    }
}