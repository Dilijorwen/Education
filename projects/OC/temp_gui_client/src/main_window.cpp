#include "main_window.h"

#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QWidget>
#include <QUrl>
#include <QTimeZone>

#include <QtCharts/QChart>
#include <QtCharts/QValueAxis>

MainWindow::MainWindow(QWidget* parent) : QMainWindow(parent) {
    setupUi();
    wire();

    pollTimer_.setInterval(2000);
    pollTimer_.start();

    requestAll();
}

void MainWindow::setupUi() {
    auto* root = new QWidget(this);
    auto* v = new QVBoxLayout(root);

    // base url
    {
        auto* row = new QHBoxLayout();
        row->addWidget(new QLabel("Server URL:", root));

        baseUrlEdit_ = new QLineEdit("http://localhost:8080", root);
        row->addWidget(baseUrlEdit_);

        auto* apply = new QPushButton("Apply", root);
        row->addWidget(apply);
        connect(apply, &QPushButton::clicked, this, [this]() {
            api_.setBaseUrl(QUrl(baseUrlEdit_->text().trimmed()));
            requestAll();
        });

        v->addLayout(row);
    }

    // current
    {
        auto* row = new QHBoxLayout();
        currentLabel_ = new QLabel("Current: —", root);
        currentTsLabel_ = new QLabel("—", root);
        row->addWidget(currentLabel_);
        row->addStretch(1);
        row->addWidget(currentTsLabel_);
        v->addLayout(row);
    }

    // controls
    {
        auto* row = new QHBoxLayout();

        fromEdit_ = new QDateTimeEdit(QDateTime::currentDateTimeUtc().addSecs(-3600), root);
        toEdit_   = new QDateTimeEdit(QDateTime::currentDateTimeUtc(), root);

        fromEdit_->setDisplayFormat("yyyy-MM-dd HH:mm:ss");
        toEdit_->setDisplayFormat("yyyy-MM-dd HH:mm:ss");

        fromEdit_->setTimeZone(QTimeZone::utc());
        toEdit_->setTimeZone(QTimeZone::utc());

        bucketBox_ = new QComboBox(root);
        bucketBox_->addItems({"raw", "hour", "day"});

        auto* refresh = new QPushButton("Refresh", root);
        connect(refresh, &QPushButton::clicked, this, [this]() { requestAll(); });

        row->addWidget(new QLabel("From (UTC):", root));
        row->addWidget(fromEdit_);
        row->addWidget(new QLabel("To (UTC):", root));
        row->addWidget(toEdit_);
        row->addWidget(new QLabel("Bucket:", root));
        row->addWidget(bucketBox_);
        row->addWidget(refresh);

        v->addLayout(row);
    }

    // stats label
    statsLabel_ = new QLabel("Stats: —", root);
    v->addWidget(statsLabel_);

    // chart
    series_ = new QLineSeries(root);
    auto* chart = new QChart();
    chart->addSeries(series_);
    chart->legend()->hide();
    chart->setTitle("Temperature");

    auto* axX = new QValueAxis();
    axX->setTitleText("t (ms)");
    auto* axY = new QValueAxis();
    axY->setTitleText("temp (C)");

    chart->addAxis(axX, Qt::AlignBottom);
    chart->addAxis(axY, Qt::AlignLeft);

    series_->attachAxis(axX);
    series_->attachAxis(axY);

    chartView_ = new QChartView(chart, root);
    chartView_->setMinimumHeight(360);

    v->addWidget(chartView_);

    setCentralWidget(root);
    resize(1100, 650);
    setWindowTitle("Temp GUI Client");
}

void MainWindow::wire() {
    connect(&pollTimer_, &QTimer::timeout, this, [this]() {
        api_.getCurrent();
    });

    connect(&api_, &ApiClient::currentReady, this, [this](const CurrentDTO& cur) {
        currentLabel_->setText(QString("Current: %1 °C").arg(cur.temp_c, 0, 'f', 2));
        currentTsLabel_->setText(QString("ts=%1").arg(cur.ts_ms));
    });

    connect(&api_, &ApiClient::statsReady, this, [this](const StatsDTO& st) {
        statsLabel_->setText(
            QString("Stats (%1): count=%2 min=%3 max=%4 avg=%5")
                .arg(st.bucket)
                .arg(st.count)
                .arg(st.min_v, 0, 'f', 2)
                .arg(st.max_v, 0, 'f', 2)
                .arg(st.avg_v, 0, 'f', 2)
        );
    });

    connect(&api_, &ApiClient::seriesReady, this, [this](const QString&, const QList<PointDTO>& pts) {
        series_->clear();
        if (pts.isEmpty()) return;

        for (const auto& p : pts) {
            series_->append((qreal)p.t_ms, (qreal)p.v);
        }

        // autoscale axes
        auto* chart = chartView_->chart();
        auto axesX = chart->axes(Qt::Horizontal);
        auto axesY = chart->axes(Qt::Vertical);
        if (!axesX.isEmpty() && !axesY.isEmpty()) {
            auto* axX = qobject_cast<QValueAxis*>(axesX.first());
            auto* axY = qobject_cast<QValueAxis*>(axesY.first());

            qint64 minT = pts.first().t_ms;
            qint64 maxT = pts.last().t_ms;

            double minV = pts.first().v;
            double maxV = pts.first().v;
            for (const auto& p : pts) {
                if (p.v < minV) minV = p.v;
                if (p.v > maxV) maxV = p.v;
            }

            if (axX) axX->setRange((qreal)minT, (qreal)maxT);

            if (axY) {
                if (maxV == minV) { maxV += 1.0; minV -= 1.0; }
                axY->setRange(minV, maxV);
            }
        }
    });

    connect(&api_, &ApiClient::errorOccured, this, [this](const QString& msg) {
        setWindowTitle("Temp GUI Client [ERROR: " + msg.left(80) + "]");
    });
}

qint64 MainWindow::ms(const QDateTime& dt) const {
    return dt.toMSecsSinceEpoch();
}

void MainWindow::requestAll() {
    api_.setBaseUrl(QUrl(baseUrlEdit_->text().trimmed()));

    const qint64 from = ms(fromEdit_->dateTime());
    const qint64 to = ms(toEdit_->dateTime());
    const QString bucket = bucketBox_->currentText();

    api_.getCurrent();
    api_.getStats(from, to, bucket);

    const int limit = 5000;
    api_.getSeries(from, to, bucket, limit);
}
