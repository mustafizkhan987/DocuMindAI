package com.documind.ai.ui.screens.documents

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.documind.ai.ui.components.DocumentCard

@Composable
fun DocumentsScreen(
    viewModel: DocumentsViewModel = viewModel(),
    onNavigateToUpload: () -> Unit = {},
    onNavigateToDocument: (String) -> Unit = {}
) {
    var searchQuery by remember { mutableStateOf("") }
    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(scrollState)
    ) {
        Text(
            text = "Documents",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.onBackground
        )
        
        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            placeholder = { Text("Search documents (Not yet connected)") },
            leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 16.dp),
            singleLine = true,
            enabled = false
        )
        
        Spacer(modifier = Modifier.height(16.dp))

        // Demo UI for Documents list
        DocumentCard(
            title = "Invoice ABC Traders (Sample)",
            subtitle = "28 Sep 2026",
            amount = "₹12,450.00",
            status = "Information Found"
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        DocumentCard(
            title = "Utility Bill (Sample)",
            subtitle = "25 Sep 2026",
            amount = "₹1,200.00",
            status = "Information Found"
        )

        Spacer(modifier = Modifier.height(8.dp))
        
        DocumentCard(
            title = "Purchase Order (Sample)",
            subtitle = "15 Sep 2026",
            amount = "₹45,000.00",
            status = "Information Found"
        )
    }
}
