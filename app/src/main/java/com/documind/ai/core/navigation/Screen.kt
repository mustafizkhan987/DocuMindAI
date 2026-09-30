package com.documind.ai.core.navigation

/**
 * Screen routes and metadata for Jetpack Compose navigation.
 */
sealed class Screen(val route: String, val title: String) {
    object Home : Screen("home", "Home")
    object Documents : Screen("documents", "Documents")
    object Settings : Screen("settings", "Settings")
    object Foundation : Screen("foundation", "Overview")
}
