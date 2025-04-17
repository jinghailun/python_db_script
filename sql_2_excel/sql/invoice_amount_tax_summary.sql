

with temporary_part_tax as (select tci.search_serial as invoice,
#                                    tso.id            as order_id,
                                   tso.search_serial as order_id,
                                   tci.amount        as invoice_amount,
                                   tci.qb_amount     as qb_amount,
                                   tp.id             as part_id,
                                   tptp.tax_region_id,
                                   ttr.tax_type,
                                   tptp.rate,
                                   tptp.taxable_amount,
                                   tptp.price,
                                   tci.created_date  as invoice_date
                            from tbl_part_tax_price tptp
                                     join tbl_part tp on tptp.part_id = tp.id
                                     join tbl_tax_region ttr on tptp.tax_region_id = ttr.id
                                     join tbl_order tso on tp.order_id = tso.id
                                     join tbl_customer_invoice tci on tci.order_id = tso.id
                            where
                              tptp.part_id is not null
                              and date(tci.created_date) >= '{{replace1}}' and date(tci.created_date) < '{{replace2}}'
                              and tci.status <> 'ABORTED'
                              and tp.status = 'ACTIVE')

SELECT invoice,
       invoice_date,
       order_id,
       ROUND(max(invoice_amount) / 10000, 2)                                     AS subtotal,
       SUM(CASE WHEN tax_type = 'CAGST' THEN ROUND(price / 10000, 2) ELSE 0 END) AS total_gst,
       SUM(CASE WHEN tax_type = 'CAPST' THEN ROUND(price / 10000, 2) ELSE 0 END) AS total_pst,
       ROUND(max(qb_amount) / 100, 2)                                            AS total_amount
FROM temporary_part_tax
GROUP BY order_id, invoice, invoice_date
ORDER BY invoice;