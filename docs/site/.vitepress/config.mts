import { defineConfig } from 'vitepress'

export default defineConfig({
    title: "NanaSQLite",
    description: "Ultra-fast SQLite dict wrapper for Python",
    base: '/NanaSQLite/',
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
                text: 'ガイド',
                items: [
                    { text: '導入ガイド', link: '/guide' },
                    { text: '非同期サポート', link: '/async_guide' },
                    { text: 'トランザクション', link: '/transaction_guide' },
                    { text: 'エラーハンドリング', link: '/error_handling' },
                    { text: '性能・最適化', link: '/performance_tuning' },
                    { text: 'ベストプラクティス', link: '/best_practices' }
                ]
            },
            {
                text: 'APIリファレンス',
                items: [
                    { text: 'NanaSQLite (同期)', link: '/api_sync' },
                    { text: 'AsyncNanaSQLite (非同期)', link: '/api_async' },
                    { text: 'クイックリファレンス', link: '/quick_reference' }
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
                        text: 'Guide',
                        items: [
                            { text: 'Getting Started', link: '/en/guide' },
                            { text: 'Async Support', link: '/en/async_guide' },
                            { text: 'Transactions', link: '/en/transaction_guide' },
                            { text: 'Error Handling', link: '/en/error_handling' },
                            { text: 'Performance', link: '/en/performance_tuning' },
                            { text: 'Best Practices', link: '/en/best_practices' }
                        ]
                    },
                    {
                        text: 'API Reference',
                        items: [
                            { text: 'NanaSQLite (Sync)', link: '/en/api_sync' },
                            { text: 'AsyncNanaSQLite (Async)', link: '/en/api_async' },
                            { text: 'Quick Reference', link: '/en/quick_reference' }
                        ]
                    }
                ]
            }
        }
    }
})

