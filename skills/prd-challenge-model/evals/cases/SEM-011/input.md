# Technical design only

采用 Kotlin 与 Jetpack Compose。客户端通过 Retrofit 调用 `/v2/profile`，数据写入 PostgreSQL，并使用 Redis 缓存 10 分钟。Repository 使用依赖注入，接口返回 DTO 后映射为领域对象。
