"""
NanaSQLite Exception Classes

カスタム例外クラスを定義し、エラーハンドリングを統一する。
"""


class NanaSQLiteError(Exception):
    """
    NanaSQLiteの基底例外クラス

    すべてのNanaSQLite固有の例外はこのクラスを継承する。
    """

    pass


class NanaSQLiteValidationError(NanaSQLiteError):
    """
    バリデーションエラー

    不正な入力値やパラメータに対して発生する。

    Examples:
        - 不正なテーブル名やカラム名
        - 不正なSQL識別子
        - パラメータの型エラー
    """

    pass


class NanaSQLiteDatabaseError(NanaSQLiteError):
    """
    データベース操作エラー

    SQLite/APSWのデータベース操作で発生するエラーをラップ。

    Examples:
        - データベースロック
        - ディスク容量不足
        - ファイル権限エラー
        - SQL構文エラー
    """

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class NanaSQLiteTransactionError(NanaSQLiteError):
    """
    トランザクション関連エラー

    トランザクションの開始、コミット、ロールバックで発生するエラー。

    Examples:
        - ネストしたトランザクションの試み
        - トランザクション外でのコミット/ロールバック
        - トランザクション中の接続クローズ
    """

    pass


class NanaSQLiteConnectionError(NanaSQLiteError):
    """
    接続エラー

    データベース接続の作成や管理で発生するエラー。

    Examples:
        - 閉じられた接続の使用
        - 接続の初期化失敗
        - 孤立した子インスタンスの使用
    """

    pass


class NanaSQLiteClosedError(NanaSQLiteConnectionError):
    """
    Closed instance error / クローズ済みエラー

    Occurs when operating on a closed instance, or on a child instance whose parent has been closed.
    閉じられたインスタンスや、親が閉じられた子インスタンスを操作しようとした時に発生。
    """

    pass


class NanaSQLiteLockError(NanaSQLiteError):
    """
    ロック取得エラー

    データベースロックの取得に失敗した場合に発生。

    Examples:
        - ロック取得タイムアウト
        - デッドロック検出
    """

    pass


class NanaSQLiteCacheError(NanaSQLiteError):
    """
    キャッシュ関連エラー

    キャッシュの操作で発生するエラー。

    Examples:
        - キャッシュサイズ超過
        - キャッシュの不整合
    """

    pass
