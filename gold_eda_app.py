import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class GoldEDAApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Gold EDA App')
        self.df = None
        self.filtered_df = None
        self.filter_vars = {}
        self.filter_widgets = {}
        self.create_widgets()

    def create_widgets(self):
        self.load_btn = tk.Button(self.root, text='Загрузить CSV', command=self.load_csv)
        self.load_btn.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.info_label = tk.Label(self.root, text='Датасет не загружен.')
        self.info_label.grid(row=1, column=0, columnspan=3, sticky='w', padx=10)
        self.filters_frame = tk.LabelFrame(self.root, text='Фильтрация данных')
        self.filters_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky='ew')
        self.filter_btn = tk.Button(self.root, text='Показать фильтрованные данные', command=self.show_filtered_data, state='disabled')
        self.filter_btn.grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.recommend_btn = tk.Button(self.root, text='Вывод рекомендаций', command=self.show_recommendations, state='disabled')
        self.recommend_btn.grid(row=3, column=1, padx=10, pady=10, sticky='w')
        self.visual_btn = tk.Button(self.root, text='Визуализация данных', command=self.show_visualization, state='disabled')
        self.visual_btn.grid(row=3, column=2, padx=10, pady=10, sticky='w')

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if not file_path:
            return
        try:
            self.df = pd.read_csv(file_path)
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось загрузить файл: {e}')
            return
        if self.df is not None:
            # Удаляю наполнение главного выпадающего списка годов
            # if 'date' in self.df.columns:
            #     self.df['year'] = pd.to_datetime(self.df['date']).dt.year
            # years = sorted(pd.Series(self.df['year']).dropna().unique()) if 'year' in self.df.columns else []
            # self.year_main_combo['values'] = ['Все'] + [str(y) for y in years]
            # self.year_main_var.set('Все')
            self.info_label.config(text=f'Файл: {file_path}\nСтрок: {self.df.shape[0]}, Столбцов: {self.df.shape[1]}\nСтолбцы: {', '.join(self.df.columns)}')
            self.create_filter_widgets()
            self.filter_btn.config(state='normal')
            self.recommend_btn.config(state='normal')
            self.visual_btn.config(state='normal')
        else:
            self.info_label.config(text='Ошибка загрузки файла.')

    def create_filter_widgets(self):
        for widget in self.filters_frame.winfo_children():
            widget.destroy()
        self.filter_vars.clear()
        self.filter_widgets.clear()
        if self.df is None:
            return
        row = 0
        print('Столбцы датафрейма:', list(self.df.columns))  # Для отладки
        for col in self.df.columns:
            col_clean = col.strip().lower()
            if col_clean == 'date':
                years = sorted(set(int(y) for y in pd.to_datetime(self.df[col], errors='coerce').dt.year.dropna().unique()))
                print('Фильтр по date (годы):', years)  # Для отладки
                var = tk.StringVar()
                var.set('Все')
                self.filter_vars['date_year'] = var
                label = tk.Label(self.filters_frame, text='date')
                label.grid(row=row, column=0, sticky='w', padx=5, pady=2)
                combo = ttk.Combobox(self.filters_frame, textvariable=var, values=['Все'] + [str(y) for y in years], state='readonly')
                combo.grid(row=row, column=1, sticky='w', padx=5, pady=2)
                self.filter_widgets['date_year'] = combo
                row += 1
                continue
            if col_clean in ['date', 'year', 'month', 'months']:
                continue
            if self.df[col].nunique() < 50 or self.df[col].dtype == 'object':
                values = sorted(self.df[col].dropna().unique())
                var = tk.StringVar()
                var.set('Все')
                self.filter_vars[col] = var
                label = tk.Label(self.filters_frame, text=col)
                label.grid(row=row, column=0, sticky='w', padx=5, pady=2)
                combo = ttk.Combobox(self.filters_frame, textvariable=var, values=['Все'] + [str(v) for v in values], state='readonly')
                combo.grid(row=row, column=1, sticky='w', padx=5, pady=2)
                self.filter_widgets[col] = combo
                row += 1

    def get_filtered_df(self):
        if self.df is None:
            return None
        df = self.df.copy()
        # Найти столбец с датой независимо от регистра и пробелов
        date_col = next((c for c in df.columns if c.strip().lower() == 'date'), None)
        if 'date_year' in self.filter_vars and date_col is not None:
            y = self.filter_vars['date_year'].get()
            if y != 'Все' and y.isdigit():
                df = df[pd.to_datetime(df[date_col], errors='coerce').dt.year == int(y)]
        # Остальные фильтры
        for col, var in self.filter_vars.items():
            if col == 'date_year':
                continue
            val = var.get()
            if val != 'Все':
                df = df[df[col].astype(str) == val]
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        return df

    def show_filtered_data(self):
        self.filtered_df = self.get_filtered_df()
        if self.filtered_df is None or self.filtered_df.empty:
            messagebox.showinfo('Результат', 'Нет данных для отображения.')
            return
        win = tk.Toplevel(self.root)
        win.title('Результаты фильтрации')
        frame = tk.Frame(win)
        frame.pack(fill='both', expand=True)
        cols = list(self.filtered_df.columns)
        tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')
        for _, row in self.filtered_df.head(100).iterrows():
            tree.insert('', 'end', values=[row[col] for col in cols])
        # Перемещаю вертикальный скроллбар вправо от таблицы
        tree.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side='right', fill='y')
        tk.Label(win, text='Показаны первые 100 строк.').pack()

    def show_recommendations(self):
        df = self.get_filtered_df()
        if df is None or df.empty:
            messagebox.showinfo('Рекомендации', 'Нет данных для анализа.')
            return
        recs = []
        if 'close' in df.columns:
            close_series = pd.Series(df['close'])
            mean_price = float(close_series.mean())
            median_price = float(close_series.median())
            min_price = float(close_series.min())
            max_price = float(close_series.max())
            recs.append(f'Средняя цена закрытия: {mean_price:.2f}')
            recs.append(f'Медианная цена закрытия: {median_price:.2f}')
            recs.append(f'Минимальная цена: {min_price:.2f}')
            recs.append(f'Максимальная цена: {max_price:.2f}')
            if mean_price > median_price:
                recs.append('Рынок склонен к росту (средняя цена выше медианы).')
            else:
                recs.append('Рынок склонен к стабильности или снижению (медиана выше средней).')
        if 'volume' in df.columns:
            mean_vol = float(df['volume'].mean())
            recs.append(f'Средний объём торгов: {mean_vol:.2f}')
        recs.append('\nПортрет типичного потребителя золота:')
        recs.append('— Возраст: преимущественно от 35 лет и старше, но встречаются и более молодые инвесторы')
        recs.append('— Пол: интерес к золоту проявляют как мужчины, так и женщины, однако мужчины могут быть более активны')
        recs.append('— Образование: чаще всего высшее, нередко в области экономики или финансов')
        recs.append('— Доход: средний и выше среднего, так как приобретение золота требует значительных вложений')
        recs.append('— Золото рассматривается как средство сохранения капитала и защиты от инфляции, а не как источник дохода')
        recs.append('— Предпочтение долгосрочным инвестициям, а не спекуляциям')
        recs.append('— Склонность к осторожности и консерватизму, избегание чрезмерных рисков')
        recs.append('— Доверие к традиционным инструментам: предпочтение физического золота (слитки, монеты) перед производными')
        win = tk.Toplevel(self.root)
        win.title('Рекомендации для бизнеса')
        text = tk.Text(win, wrap='word', width=80, height=25)
        text.pack(fill='both', expand=True)
        text.insert('1.0', '\n'.join(recs))
        text.config(state='disabled')
        btn = tk.Button(win, text='Закрыть', command=win.destroy)
        btn.pack(pady=5)

    def show_visualization(self):
        df = self.get_filtered_df()
        if df is None or df.empty:
            messagebox.showinfo('Визуализация', 'Нет данных для визуализации.')
            return
        win = tk.Toplevel(self.root)
        win.title('Визуализация данных')
        tk.Label(win, text='Выберите тип графика:').pack(pady=5)
        chart_type = tk.StringVar(value='Линейный график')
        options = ['Линейный график', 'Гистограмма', 'Boxplot']
        combo = ttk.Combobox(win, textvariable=chart_type, values=options, state='readonly')
        combo.pack(pady=5)
        def plot():
            fig, ax = plt.subplots(figsize=(7,4))
            close_col = None
            for col in df.columns:
                if col.lower() == 'close':
                    close_col = col
                    break
            if close_col is None:
                messagebox.showinfo('Визуализация', f'Нет столбца "close" для визуализации.\nДоступные столбцы: {list(df.columns)}')
                return
            if chart_type.get() == 'Линейный график':
                if 'date' in df.columns:
                    x = pd.to_datetime(df['date'])
                else:
                    x = range(len(df))
                ax.plot(x, df[close_col], label='Цена закрытия', color='gold')
                ax.set_xlabel('Дата' if 'date' in df.columns else 'Индекс')
                ax.set_ylabel('Цена закрытия')
                ax.set_title('Линейный график цены закрытия')
                ax.grid(True, alpha=0.3)
            elif chart_type.get() == 'Гистограмма':
                ax.hist(pd.Series(df[close_col]).dropna(), bins=30, color='gold', edgecolor='black', alpha=0.7)
                ax.set_xlabel('Цена закрытия')
                ax.set_ylabel('Частота')
                ax.set_title('Гистограмма цены закрытия')
                ax.grid(True, alpha=0.3)
            elif chart_type.get() == 'Boxplot':
                ax.boxplot(pd.Series(df[close_col]).dropna(), vert=True, patch_artist=True, boxprops=dict(facecolor='gold'))
                ax.set_ylabel('Цена закрытия')
                ax.set_title('Boxplot цены закрытия')
                ax.grid(True, alpha=0.3, axis='y')
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=win)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        btn = tk.Button(win, text='Построить график', command=plot)
        btn.pack(pady=5)
        tk.Button(win, text='Закрыть', command=win.destroy).pack(pady=5)

    # def on_main_year_change(self, event=None):
    #     # Синхронизируем выбор года на главной форме с фильтром по году в фильтрах
    #     if 'year' in self.filter_vars:
    #         self.filter_vars['year'].set(self.year_main_var.get())
    #         # Обновляем месяцы, если есть
    #         if 'months' in self.filter_widgets and hasattr(self.filter_widgets['months'], 'delete'):
    #             self.filter_widgets['months'].delete(0, tk.END)
    #             # Триггерим обновление месяцев
    #             if hasattr(self.filter_vars['year'], 'trace_add'):
    #                 for cb in self.filter_vars['year'].trace_info():
    #                     self.filter_vars['year'].trace_remove(cb[0], cb[1])
    #                 self.filter_vars['year'].trace_add('write', lambda *a: None)
    #         self.create_filter_widgets()

if __name__ == '__main__':
    root = tk.Tk()
    app = GoldEDAApp(root)
    root.mainloop() 