package com.documind.ai.ui.screens.documents

import com.documind.ai.domain.model.Document

data class DocumentsUiState(
    val isUploading: Boolean = false,
    val uploadError: String? = null,
    val uploadedDocument: Document? = null
)
