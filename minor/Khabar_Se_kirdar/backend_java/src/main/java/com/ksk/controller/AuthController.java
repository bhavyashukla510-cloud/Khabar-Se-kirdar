package com.ksk.controller;

import com.ksk.model.User;
import com.ksk.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin("*")
public class AuthController {

    @Autowired
    private UserRepository userRepository;

     @GetMapping("/status")
    public String status() {
        return "Auth controller is working!";
    }
    
    @PostMapping("/register")
    public User register(@RequestBody User user) {
        return userRepository.save(user);
    }

    @PostMapping("/login")
    public String login(@RequestBody User user) {

        User existing = userRepository
                .findByEmail(user.getEmail())
                .orElseThrow(() -> new RuntimeException("User not found"));

        if (!existing.getPassword().equals(user.getPassword())) {
            throw new RuntimeException("Invalid password");
        }

        return "Login successful";
    }
}
