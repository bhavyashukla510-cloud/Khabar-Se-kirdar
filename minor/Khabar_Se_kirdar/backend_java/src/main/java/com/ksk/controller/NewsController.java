package com.ksk.controller;

import com.ksk.model.News;
import com.ksk.repository.NewsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/news")
@CrossOrigin("*")
public class NewsController {

    @Autowired
    private NewsRepository newsRepository;

    @GetMapping
    public List<News> getAllNews() {
        return newsRepository.findAll();
    }

    @PostMapping
    public News addNews(@RequestBody News news) {
        return newsRepository.save(news);
    }
}
