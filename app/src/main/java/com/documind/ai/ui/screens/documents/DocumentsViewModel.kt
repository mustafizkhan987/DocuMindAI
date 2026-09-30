package com.documind.ai.ui.screens.documents

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.documind.ai.core.common.Result
import com.documind.ai.core.network.NetworkModule
import com.documind.ai.data.repository.DocumentRepositoryImpl
import com.documind.ai.domain.repository.DocumentRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.io.ByteArrayOutputStream
import java.io.InputStream

class DocumentsViewModel(
    private val repository: DocumentRepository = DocumentRepositoryImpl(NetworkModule.provideDocuMindApi())
) : ViewModel() {

    private val _uiState = MutableStateFlow(DocumentsUiState())
    val uiState: StateFlow<DocumentsUiState> = _uiState.asStateFlow()

    fun resetUploadState() {
        _uiState.update { it.copy(isUploading = false, uploadError = null, uploadedDocument = null) }
    }

    fun uploadDocument(uri: Uri, context: Context) {
        viewModelScope.launch {
            _uiState.update { it.copy(isUploading = true, uploadError = null, uploadedDocument = null) }
            
            try {
                val contentResolver = context.contentResolver
                val mimeType = contentResolver.getType(uri) ?: "application/octet-stream"
                var fileName = "unknown"
                
                contentResolver.query(uri, null, null, null, null)?.use { cursor ->
                    if (cursor.moveToFirst()) {
                        val displayNameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                        if (displayNameIndex != -1) {
                            fileName = cursor.getString(displayNameIndex)
                        }
                    }
                }
                
                val inputStream: InputStream? = contentResolver.openInputStream(uri)
                if (inputStream == null) {
                    _uiState.update { it.copy(isUploading = false, uploadError = "Failed to open file") }
                    return@launch
                }
                
                val byteArrayOutputStream = ByteArrayOutputStream()
                val buffer = ByteArray(1024)
                var len: Int
                while (inputStream.read(buffer).also { len = it } != -1) {
                    byteArrayOutputStream.write(buffer, 0, len)
                }
                val fileBytes = byteArrayOutputStream.toByteArray()
                inputStream.close()
                
                when (val result = repository.uploadDocument(fileBytes, fileName, mimeType)) {
                    is Result.Success -> {
                        _uiState.update { it.copy(isUploading = false, uploadedDocument = result.data) }
                    }
                    is Result.Error -> {
                        _uiState.update { it.copy(isUploading = false, uploadError = result.message) }
                    }
                    is Result.Loading -> {}
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(isUploading = false, uploadError = e.localizedMessage) }
            }
        }
    }
}
