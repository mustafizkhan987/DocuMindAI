package com.documind.ai.core.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Layers
import androidx.compose.ui.graphics.vector.ImageVector

sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    object Home : Screen("home", "Home", Icons.Default.Home)
    object Documents : Screen("documents", "Documents", Icons.Default.Description)
    object Settings : Screen("settings", "Settings", Icons.Default.Settings)
    object Upload : Screen("upload", "Upload", Icons.Default.Description)
    object Processing : Screen("processing/{documentId}", "Processing", Icons.Default.Description) {
        fun createRoute(documentId: String) = "processing/$documentId"
    }
    object DocumentResult : Screen("document_result/{documentId}", "Result", Icons.Default.Description) {
        fun createRoute(documentId: String) = "document_result/$documentId"
    }
    object About : Screen("about", "About", Icons.Default.Description)
    object Foundation : Screen("foundation", "Foundation", Icons.Default.Layers)
}
