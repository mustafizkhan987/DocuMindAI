package com.documind.ai.ui.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import com.documind.ai.core.navigation.Screen

/**
 * Material 3 Bottom Navigation Bar for DocuMind AI.
 */
@Composable
fun AppBottomNavigation(
    currentRoute: String?,
    onNavigate: (Screen) -> Unit
) {
    val items = listOf(
        Screen.Home,
        Screen.Documents,
        Screen.Settings,
        Screen.Foundation
    )

    NavigationBar(
        containerColor = Color(0xFF141A29),
        contentColor = Color.White
    ) {
        items.forEach { screen ->
            val selected = currentRoute == screen.route
            val icon = when (screen) {
                Screen.Home -> Icons.Default.Home
                Screen.Documents -> Icons.Default.Description
                Screen.Settings -> Icons.Default.Settings
                Screen.Foundation -> Icons.Default.Info
            }

            NavigationBarItem(
                selected = selected,
                onClick = { onNavigate(screen) },
                icon = { Icon(imageVector = icon, contentDescription = screen.title) },
                label = { Text(screen.title) },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = Color(0xFF00E676),
                    selectedTextColor = Color(0xFF00E676),
                    indicatorColor = Color(0xFF1E293B),
                    unselectedIconColor = Color.Gray,
                    unselectedTextColor = Color.Gray
                )
            )
        }
    }
}
