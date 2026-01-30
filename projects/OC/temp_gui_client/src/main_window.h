#pragma once
#include <QMainWindow>
#include <QDateTimeEdit>
#include <QLabel>
#include <QLineEdit>
#include <QComboBox>
#include <QPushButton>
#include <QTimer>

#include <QtCharts/QChartView>
#include <QtCharts/QLineSeries>

#include "api_client.h"

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget* parent = nullptr);

private:
    ApiClient api_;

    QLineEdit* baseUrlEdit_ = nullptr;

    QLabel* currentLabel_ = nullptr;
    QLabel* currentTsLabel_ = nullptr;

    QDateTimeEdit* fromEdit_ = nullptr;
    QDateTimeEdit* toEdit_ = nullptr;
    QComboBox* bucketBox_ = nullptr;

    QLabel* statsLabel_ = nullptr;

    QLineSeries* series_ = nullptr;
    QChartView* chartView_ = nullptr;

    QTimer pollTimer_;

    void setupUi();
    void wire();

    void requestAll();
    qint64 ms(const QDateTime& dt) const;
};
