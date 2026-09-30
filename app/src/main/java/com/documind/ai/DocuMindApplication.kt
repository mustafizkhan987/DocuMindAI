package com.documind.ai

import android.app.Application

/**
 * DocuMind AI — Application Class
 *
 * Task 3: Android Application Foundation
 *
 * Base Application class for global application initialization,
 * logging, and future dependency injection (e.g. Hilt/Koin).
 */
class DocuMindApplication : Application() {

    override fun onCreate() {
        super.onCreate()
        // Initialize global app configuration, logging, or DI modules here
    }
}
