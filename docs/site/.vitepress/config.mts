import { defineConfig } from 'vitepress'

export default defineConfig({
    title: "NanaSQLite",
    description: "Ultra-fast SQLite dict wrapper for Python",
    base: '/',
    head: [
        ['link', { rel: 'icon', href: '/logo.svg' }]
    ],
    themeConfig: {
        logo: '/logo.svg',
        nav: [
            { text: 'ホーム', link: '/' },
            { text: 'ガイド', link: '/guide' },
            { text: 'APIリファレンス', link: '/api_sync' }
        ],
        sidebar: [
            {
                text: 'はじめに',
                items: [
                    { text: '導入ガイド', link: '/guide' },
                    { text: 'クイックリファレンス', link: '/quick_reference' },
                    { text: '変更履歴 (Changelog)', link: '/changelog' }
                ]
            },
            {
                text: '基本機能',
                items: [
                    { text: '非同期サポート', link: '/async_guide' },
                    { text: 'トランザクション', link: '/transaction_guide' },
                    { text: 'バリデーション', link: '/validation_guide' },
                    { text: 'エラーハンドリング', link: '/error_handling' }
                ]
            },
            {
                text: '高度な機能',
                items: [
                    { text: 'キャッシュ戦略', link: '/cache_strategies' },
                    { text: '暗号化', link: '/encryption_guide' },
                    { text: 'V2 アーキテクチャ', link: '/v2_architecture' }
                ]
            },
            {
                text: '運用・セキュリティ',
                items: [
                    { text: '性能・最適化', link: '/performance_tuning' },
                    { text: 'ベストプラクティス', link: '/best_practices' },
                    { text: 'セキュリティ監査', link: '/security_audit' }
                ]
            },
            {
                text: 'APIリファレンス',
                items: [
                    { text: 'NanaSQLite (同期)', link: '/api_sync' },
                    { text: 'AsyncNanaSQLite (非同期)', link: '/api_async' },
                    { text: '例外クラス', link: '/exceptions' }
                ]
            }
        ],
        socialLinks: [
            { icon: 'github', link: 'https://github.com/disnana/NanaSQLite' }
        ]
    },
    locales: {
        root: {
            label: '日本語',
            lang: 'ja-JP'
        },
        en: {
            label: 'English',
            lang: 'en-US',
            link: '/en/',
            themeConfig: {
                nav: [
                    { text: 'Home', link: '/en/' },
                    { text: 'Guide', link: '/en/guide' },
                    { text: 'API Reference', link: '/en/api_sync' }
                ],
                sidebar: [
                    {
                        text: 'Getting Started',
                        items: [
                            { text: 'Tutorial', link: '/en/guide' },
                            { text: 'Quick Reference', link: '/en/quick_reference' },
                            { text: 'Changelog', link: '/en/changelog' }
                        ]
                    },
                    {
                        text: 'Core Features',
                        items: [
                            { text: 'Async Support', link: '/en/async_guide' },
                            { text: 'Transactions', link: '/en/transaction_guide' },
                            { text: 'Validation', link: '/en/validation_guide' },
                            { text: 'Error Handling', link: '/en/error_handling' }
                        ]
                    },
                    {
                        text: 'Advanced Features',
                        items: [
                            { text: 'Cache Strategies', link: '/en/cache_strategies' },
                            { text: 'Encryption', link: '/en/encryption_guide' },
                            { text: 'V2 Architecture', link: '/en/v2_architecture' }
                        ]
                    },
                    {
                        text: 'Operations & Security',
                        items: [
                            { text: 'Performance Tuning', link: '/en/performance_tuning' },
                            { text: 'Best Practices', link: '/en/best_practices' },
                            { text: 'Security Audit', link: '/en/security_audit' }
                        ]
                    },
                    {
                        text: 'API Reference',
                        items: [
                            { text: 'NanaSQLite (Sync)', link: '/en/api_sync' },
                            { text: 'AsyncNanaSQLite (Async)', link: '/en/api_async' },
                            { text: 'Exceptions', link: '/en/exceptions' }
                        ]
                    }
                ]
            }
        }
    }
})
