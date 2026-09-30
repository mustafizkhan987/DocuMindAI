package com.documind.ai.network

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * DocuMind AI — Network Configuration
 *
 * Task 1: Project Foundation
 *
 * Configures Retrofit + OkHttp for communication with the FastAPI backend.
 *
 * Backend URL:
 *   - Android Emulator: http://10.0.2.2:8000/  (10.0.2.2 maps to host machine localhost)
 *   - Physical Device: http://<your-local-ip>:8000/
 *   - Production: https://api.documind.ai/ (Task 35+)
 *
 * Future tasks will add:
 *   - Authentication interceptor with JWT tokens (Task 3+)
 *   - File upload support (Task 5+)
 *   - Certificate pinning (Task 31+)
 */
object NetworkConfig {

    // Base URL comes from BuildConfig — set per build variant in build.gradle.kts
    // Debug: http://10.0.2.2:8000/
    // Release: https://api.documind.ai/
    const val BASE_URL_EMULATOR = "http://10.0.2.2:8000/"
    const val BASE_URL_LOCALHOST = "http://localhost:8000/"

    // Connection timeouts
    private const val CONNECT_TIMEOUT_SECONDS = 30L
    private const val READ_TIMEOUT_SECONDS = 60L
    private const val WRITE_TIMEOUT_SECONDS = 60L

    /**
     * Create an OkHttpClient with logging (for debug) and timeouts.
     */
    fun createOkHttpClient(enableLogging: Boolean = true): OkHttpClient {
        val builder = OkHttpClient.Builder()
            .connectTimeout(CONNECT_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(READ_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .writeTimeout(WRITE_TIMEOUT_SECONDS, TimeUnit.SECONDS)

        if (enableLogging) {
            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            builder.addInterceptor(loggingInterceptor)
        }

        return builder.build()
    }

    /**
     * Create the primary Retrofit instance for the DocuMind API.
     */
    fun createRetrofit(
        baseUrl: String = BASE_URL_EMULATOR,
        enableLogging: Boolean = true
    ): Retrofit {
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(createOkHttpClient(enableLogging))
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
}
