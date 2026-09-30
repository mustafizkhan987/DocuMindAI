package com.documind.ai.domain.repository

import com.documind.ai.core.common.Result
import com.documind.ai.domain.model.BackendHealth
import com.documind.ai.domain.model.Document
import kotlinx.coroutines.flow.Flow

/**
 * Domain repository contract interface for DocuMind AI documents and backend operations.
 */
interface DocumentRepository {
    suspend fun getBackendHealth(): Result<BackendHealth>
    fun getRecentDocuments(): Flow<List<Document>>
    suspend fun uploadDocument(fileBytes: ByteArray, fileName: String, mimeType: String): Result<Document>
}
