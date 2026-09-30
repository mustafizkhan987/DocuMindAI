package com.documind.ai.core.network

import com.documind.ai.data.remote.api.DocuMindApi
import com.documind.ai.network.NetworkConfig

/**
 * Singleton factory provider for Retrofit API instances.
 */
object ApiClient {
    val api: DocuMindApi by lazy {
        NetworkConfig.createRetrofit().create(DocuMindApi::class.java)
    }
}
