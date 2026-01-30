#pragma once
#include <QObject>
#include <QNetworkAccessManager>
#include <QUrl>

struct CurrentDTO {
    qint64 ts_ms = 0;
    double temp_c = 0.0;
};

struct StatsDTO {
    QString bucket;
    qint64 from_ms = 0;
    qint64 to_ms = 0;
    qint64 count = 0;
    double min_v = 0.0;
    double max_v = 0.0;
    double avg_v = 0.0;
};

struct PointDTO {
    qint64 t_ms = 0;
    double v = 0.0;
    qint64 n = 0;
};

class ApiClient : public QObject {
    Q_OBJECT
public:
    explicit ApiClient(QObject* parent = nullptr);

    void setBaseUrl(const QUrl& base);
    QUrl baseUrl() const;

    void getCurrent();
    void getStats(qint64 from_ms, qint64 to_ms, const QString& bucket);
    void getSeries(qint64 from_ms, qint64 to_ms, const QString& bucket, int limit);

    signals:
        void currentReady(const CurrentDTO& cur);
    void statsReady(const StatsDTO& st);
    void seriesReady(const QString& bucket, const QList<PointDTO>& pts);
    void errorOccured(const QString& msg);

private:
    QUrl base_;
    QNetworkAccessManager nam_;

    void emitNetworkError(const QString& prefix, const QByteArray& body);
};
