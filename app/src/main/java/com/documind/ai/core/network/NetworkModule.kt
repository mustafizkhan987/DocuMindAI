package com.documind.ai.core.network

import com.documind.ai.data.remote.api.DocuMindApi

/**
 * Dependency injection / provider module for Network abstractions.
 */
object NetworkModule {
    fun provideDocuMindApi(): DocuMindApi {
        return ApiClient.api
    }
}
