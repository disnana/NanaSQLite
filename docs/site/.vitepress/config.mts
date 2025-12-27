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
            { text: '導入ガイド', link: '/guide' },
            { text: '性能・最適化', link: '/performance_tuning' }
        ],
        sidebar: [
            {
                text: 'ドキュメント',
                items: [
                    { text: '導入ガイド', link: '/guide' },
                    { text: '性能・最適化', link: '/performance_tuning' },
                    { text: 'エラー・トラブル', link: '/error_handling' }
                ]
            },
            {
                text: 'API リファレンス',
                items: [
                    { text: 'Synchronous API', link: '/api_sync' },
                    { text: 'Asynchronous API', link: '/api_async' }
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
                    { text: 'Performance', link: '/en/performance_tuning' }
                ],
                sidebar: [
                    {
                        text: 'Documentation',
                        items: [
                            { text: 'Guide', link: '/en/guide' },
                            { text: 'Performance', link: '/en/performance_tuning' },
                            { text: 'Error Handling', link: '/en/error_handling' },
                            { text: 'Best Practices', link: '/en/best_practices' },
                            { text: 'Transactions', link: '/en/transaction_guide' }
                        ]
                    },
                    {
                        text: 'API Reference',
                        items: [
                            { text: 'Synchronous API', link: '/en/api_sync' },
                            { text: 'Asynchronous API', link: '/en/api_async' },
                            { text: 'Reference', link: '/en/reference' }
                        ]
                    }
                ]
            }
        }
    }
})
