# DocuMind AI ProGuard Rules
# Add project specific ProGuard rules here.

# Retrofit - keep annotations and interfaces
-keepattributes Signature
-keepattributes Exceptions
-keepattributes *Annotation*
-keep class retrofit2.** { *; }
-keep interface retrofit2.** { *; }

# Gson
-keepattributes EnclosingMethod
-keep class com.google.gson.** { *; }

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**

# DocuMind data classes
-keep class com.documind.ai.network.** { *; }
