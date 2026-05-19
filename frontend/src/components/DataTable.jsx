export default function DataTable({ columns, data, sortKey, sortOrder, onSort, children }) {
  const handleSort = (field) => {
    if (!onSort) return;
    const direction = sortKey === field && sortOrder === 'asc' ? 'desc' : 'asc';
    onSort(field, direction);
  };

  return (
    <div className="overflow-hidden rounded-3xl border border-border bg-panel shadow-xl shadow-black/10">
      <table className="w-full border-collapse text-left">
        <thead className="bg-surface text-xs uppercase tracking-[0.2em] text-muted">
          <tr>
            {columns.map((column) => (
              <th key={column.key} className="px-4 py-4">
                <button type="button" onClick={() => handleSort(column.key)} className="flex items-center gap-2 font-semibold">
                  {column.label}
                  {sortKey === column.key ? <span>{sortOrder === 'asc' ? '▲' : '▼'}</span> : null}
                </button>
              </th>
            ))}
            {children ? <th className="px-4 py-4 text-right">Actions</th> : null}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length + (children ? 1 : 0)} className="p-6 text-center text-muted">
                No records found.
              </td>
            </tr>
          ) : (
            data.map((row) => (
              <tr key={row.id} className="border-t border-border hover:bg-surface/70">
                {columns.map((column) => (
                  <td key={column.key} className="px-4 py-4 align-top text-sm text-white">
                    {column.render ? column.render(row[column.key], row) : row[column.key] ?? '-'}
                  </td>
                ))}
                {children ? <td className="px-4 py-4 text-right align-top">{children(row)}</td> : null}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
