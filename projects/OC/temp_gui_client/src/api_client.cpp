#include "api_client.h"

#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QNetworkReply>
#include <QUrlQuery>

ApiClient::ApiClient(QObject* parent) : QObject(parent) {
    base_ = QUrl("http://localhost:8080");
}

void ApiClient::setBaseUrl(const QUrl& base) { base_ = base; }
QUrl ApiClient::baseUrl() const { return base_; }

void ApiClient::emitNetworkError(const QString& prefix, const QByteArray& body) {
    QString msg = prefix;
    if (!body.isEmpty()) msg += " | " + QString::fromUtf8(body);
    emit errorOccured(msg);
}

void ApiClient::getCurrent() {
    QUrl url = base_;
    url.setPath("/api/current");

    QNetworkReply* r = nam_.get(QNetworkRequest(url));
    connect(r, &QNetworkReply::finished, this, [this, r]() {
        const QByteArray body = r->readAll();
        if (r->error() != QNetworkReply::NoError) {
            emitNetworkError("GET /api/current failed: " + r->errorString(), body);
            r->deleteLater();
            return;
        }

        const auto doc = QJsonDocument::fromJson(body);
        if (!doc.isObject()) {
            emitNetworkError("Invalid JSON for /api/current", body);
            r->deleteLater();
            return;
        }

        const QJsonObject o = doc.object();
        CurrentDTO cur;
        cur.ts_ms = (qint64)o.value("ts_ms").toVariant().toLongLong();
        cur.temp_c = o.value("temp_c").toDouble();
        emit currentReady(cur);
        r->deleteLater();
    });
}

void ApiClient::getStats(qint64 from_ms, qint64 to_ms, const QString& bucket) {
    QUrl url = base_;
    url.setPath("/api/stats");

    QUrlQuery q;
    q.addQueryItem("from", QString::number(from_ms));
    q.addQueryItem("to", QString::number(to_ms));
    q.addQueryItem("bucket", bucket);
    url.setQuery(q);

    QNetworkReply* r = nam_.get(QNetworkRequest(url));
    connect(r, &QNetworkReply::finished, this, [this, r]() {
        const QByteArray body = r->readAll();
        if (r->error() != QNetworkReply::NoError) {
            emitNetworkError("GET /api/stats failed: " + r->errorString(), body);
            r->deleteLater();
            return;
        }

        const auto doc = QJsonDocument::fromJson(body);
        if (!doc.isObject()) {
            emitNetworkError("Invalid JSON for /api/stats", body);
            r->deleteLater();
            return;
        }

        const QJsonObject o = doc.object();
        StatsDTO st;
        st.bucket = o.value("bucket").toString();
        st.from_ms = (qint64)o.value("from").toVariant().toLongLong();
        st.to_ms = (qint64)o.value("to").toVariant().toLongLong();
        st.count = (qint64)o.value("count").toVariant().toLongLong();
        st.min_v = o.value("min").toDouble();
        st.max_v = o.value("max").toDouble();
        st.avg_v = o.value("avg").toDouble();
        emit statsReady(st);
        r->deleteLater();
    });
}

void ApiClient::getSeries(qint64 from_ms, qint64 to_ms, const QString& bucket, int limit) {
    QUrl url = base_;
    url.setPath("/api/series");

    QUrlQuery q;
    q.addQueryItem("from", QString::number(from_ms));
    q.addQueryItem("to", QString::number(to_ms));
    q.addQueryItem("bucket", bucket);
    q.addQueryItem("limit", QString::number(limit));
    url.setQuery(q);

    QNetworkReply* r = nam_.get(QNetworkRequest(url));
    connect(r, &QNetworkReply::finished, this, [this, r, bucket]() {
        const QByteArray body = r->readAll();
        if (r->error() != QNetworkReply::NoError) {
            emitNetworkError("GET /api/series failed: " + r->errorString(), body);
            r->deleteLater();
            return;
        }

        const auto doc = QJsonDocument::fromJson(body);
        if (!doc.isObject()) {
            emitNetworkError("Invalid JSON for /api/series", body);
            r->deleteLater();
            return;
        }

        const QJsonObject o = doc.object();
        const QJsonArray arr = o.value("points").toArray();

        QList<PointDTO> pts;
        pts.reserve(arr.size());
        for (const auto& v : arr) {
            const QJsonObject p = v.toObject();
            PointDTO pt;
            pt.t_ms = (qint64)p.value("t").toVariant().toLongLong();
            pt.v = p.value("v").toDouble();
            pt.n = (qint64)p.value("n").toVariant().toLongLong();
            pts.push_back(pt);
        }

        emit seriesReady(bucket, pts);
        r->deleteLater();
    });
}
