package com.example.Ece.controller;

import com.alibaba.fastjson.JSONObject;
import com.example.Ece.common.Result;
import com.example.Ece.entity.ImgRecords;
import com.example.Ece.mapper.ImgRecordsMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import javax.annotation.Resource;

@RestController
@RequestMapping("/flask")
public class PredictionController {
    @Resource
    ImgRecordsMapper imgRecordsMapper;

    @Value("${app.flask-base-url}")
    private String flaskBaseUrl;

    private final RestTemplate restTemplate = new RestTemplate();

    public static class PredictRequest {
        private String startTime;
        private String weight;
        private String username;
        private String inputImg;
        private String kind;
        private String conf;

        public String getUsername() {
            return username;
        }

        public void setUsername(String username) {
            this.username = username;
        }

        public String getStartTime() {
            return startTime;
        }

        public void setStartTime(String startTime) {
            this.startTime = startTime;
        }

        public String getWeight() {
            return weight;
        }

        public void setWeight(String weight) {
            this.weight = weight;
        }

        public String getInputImg() {
            return inputImg;
        }

        public void setInputImg(String inputImg) {
            this.inputImg = inputImg;
        }

        public String getConf() {
            return conf;
        }

        public void setConf(String conf) {
            this.conf = conf;
        }

        public String getKind() {
            return kind;
        }

        public void setKind(String kind) {
            this.kind = kind;
        }
    }

    @PostMapping("/predict")
    public Result<?> predict(@RequestBody PredictRequest request) {
        if (request == null || request.getInputImg() == null || request.getInputImg().isEmpty()) {
            return Result.error("-1", "missing image url");
        } else if (request.getWeight() == null || request.getWeight().isEmpty()) {
            return Result.error("-1", "missing weight");
        }

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<PredictRequest> requestEntity = new HttpEntity<>(request, headers);

            String response = restTemplate.postForObject(buildFlaskUrl("/predictImg"), requestEntity, String.class);
            JSONObject responses = JSONObject.parseObject(response);
            if (responses.get("status").equals(400)) {
                return Result.error("-1", "Error: " + responses.get("message"));
            } else {
                ImgRecords imgRecords = new ImgRecords();
                imgRecords.setWeight(request.getWeight());
                imgRecords.setConf(request.getConf());
                imgRecords.setKind(request.getKind());
                imgRecords.setInputImg(request.getInputImg());
                imgRecords.setUsername(request.getUsername());
                imgRecords.setStartTime(request.getStartTime());
                imgRecords.setLable(String.valueOf(responses.get("label")));
                imgRecords.setConfidence(String.valueOf(responses.get("confidence")));
                imgRecords.setAllTime(String.valueOf(responses.get("allTime")));
                imgRecords.setOutImg(String.valueOf(responses.get("outImg")));
                imgRecordsMapper.insert(imgRecords);
                return Result.success(response);
            }
        } catch (Exception e) {
            return Result.error("-1", "Error: " + e.getMessage());
        }
    }

    @GetMapping("/file_names")
    public Result<?> getFileNames() {
        try {
            String response = restTemplate.getForObject(buildFlaskUrl("/file_names"), String.class);
            return Result.success(response);
        } catch (Exception e) {
            return Result.error("-1", "Error: " + e.getMessage());
        }
    }

    private String buildFlaskUrl(String path) {
        String baseUrl = flaskBaseUrl == null ? "http://127.0.0.1:5000" : flaskBaseUrl.trim();
        if (baseUrl.endsWith("/")) {
            baseUrl = baseUrl.substring(0, baseUrl.length() - 1);
        }
        return baseUrl + path;
    }
}
