package com.documind.ai.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Folder
import androidx.compose.material.icons.filled.Settings
import androidx.compose.ui.graphics.vector.ImageVector

sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    object Home : Screen("home", "Home", Icons.Default.Home)
    object Documents : Screen("documents", "Documents", Icons.Default.Folder)
    object Settings : Screen("settings", "Settings", Icons.Default.Settings)
    object Upload : Screen("upload", "Upload", Icons.Default.Home)
    object Processing : Screen("processing/{documentId}", "Processing", Icons.Default.Home) {
        fun createRoute(documentId: String) = "processing/$documentId"
    }
    object DocumentResult : Screen("result/{documentId}", "Result", Icons.Default.Home) {
        fun createRoute(documentId: String) = "result/$documentId"
    }
    object About : Screen("about", "About", Icons.Default.Home)
}
